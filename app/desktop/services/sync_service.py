from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, MutableMapping, TypedDict, TYPE_CHECKING, cast

import yaml  # type: ignore[import-untyped]

if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol

    class _YamlModule(Protocol):
        def safe_load(self, stream: str) -> Any: ...

    yaml = cast("_YamlModule", yaml)

__all__ = [
    "RunnerResult",
    "DeviceConfig",
    "SyncCommandError",
    "ConfigurationError",
    "SyncService",
]


RunnerCommand = Sequence[str]
Clock = Callable[[], datetime]


class DeviceStatus(TypedDict, total=False):
    """Serialized status snapshot for a single device."""

    last_push: str
    last_pull: str
    last_error: str | None
    last_batch: str
    last_pull_path: str
    last_manifest: dict[str, Any]


class SyncStatus(TypedDict):
    """Top-level structure persisted in ``sync/status.json``."""

    devices: Dict[str, DeviceStatus]


@dataclass(slots=True)
class RunnerResult:
    """Result container used to abstract ``subprocess.run`` outputs."""

    returncode: int
    stdout: str = ""
    stderr: str = ""


Runner = Callable[[RunnerCommand], RunnerResult]


@dataclass(slots=True)
class DeviceConfig:
    """Light-weight description of one Android executor device."""

    device_id: str
    adb_serial: str
    remote_root: str = "/sdcard/XianyuTasks"
    todo_dir: str = "Todo"
    done_dir: str = "Done"

    def normalized_remote_root(self) -> str:
        root = self.remote_root.rstrip("/")
        return root or "/"

    @property
    def remote_todo(self) -> str:
        return f"{self.normalized_remote_root()}/{self.todo_dir}"

    @property
    def remote_done(self) -> str:
        return f"{self.normalized_remote_root()}/{self.done_dir}"


class SyncCommandError(RuntimeError):
    """Wrap ADB command failures so callers can react gracefully."""

    def __init__(self, command: RunnerCommand, stderr: str):
        joined = " ".join(command)
        super().__init__(f"ADB 命令执行失败: {joined} :: {stderr.strip()}")
        self.command = list(command)
        self.stderr = stderr


class ConfigurationError(RuntimeError):
    """Raised when desktop-side configuration is missing or malformed."""


def _default_runner(command: RunnerCommand) -> RunnerResult:
    completed = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        check=False,
    )
    return RunnerResult(
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def _default_clock() -> datetime:
    return datetime.now()


class SyncService:
    """Provide push / pull orchestration between desktop and Android devices."""

    def __init__(
        self,
        workspace: Path,
        *,
        config_path: Path | None = None,
        devices: Iterable[DeviceConfig] | None = None,
        runner: Runner | None = None,
        clock: Clock | None = None,
        status_path: Path | None = None,
    ) -> None:
        self.workspace = workspace
        self.sync_root = workspace / "sync"
        self.sync_root.mkdir(parents=True, exist_ok=True)

        if devices is None:
            if config_path is None:
                raise ConfigurationError("缺少设备配置: 请提供 config_path 或 devices 列表")
            devices = self._load_devices_from_yaml(config_path)

        device_list = list(devices)
        if not device_list:
            raise ConfigurationError("设备配置为空, 请至少配置一台设备")

        self.devices: Dict[str, DeviceConfig] = {device.device_id: device for device in device_list}
        self._runner: Runner = runner or _default_runner
        self._clock: Clock = clock or _default_clock
        self.status_path = status_path or self.sync_root / "status.json"
        self.status_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ 公共接口
    def list_devices(self) -> list[DeviceConfig]:
        return list(self.devices.values())

    def push_batch(self, device_id: str, batch_dir: Path) -> None:
        device = self._ensure_device(device_id)
        if not batch_dir.exists():
            raise FileNotFoundError(f"批次目录不存在: {batch_dir}")
        if not batch_dir.is_dir():
            raise NotADirectoryError(f"批次路径并非目录: {batch_dir}")

        remote_todo = device.remote_todo
        self._exec(device, ("shell", "mkdir", "-p", remote_todo))
        self._exec(device, ("push", str(batch_dir), remote_todo))

        manifest = self._summarise_batch(batch_dir)
        self._update_status(
            device_id,
            last_push=self._clock(),
            last_error=None,
            last_batch=batch_dir.name,
            manifest=manifest,
        )

    def pull_logs(self, device_id: str) -> Path:
        device = self._ensure_device(device_id)
        timestamp = self._clock()
        target_dir = self._prepare_pull_directory(device.device_id, timestamp)

        self._exec(device, ("pull", device.remote_done, str(target_dir)))
        self._update_status(
            device_id,
            last_pull=timestamp,
            last_error=None,
            last_pull_path=str(target_dir),
        )
        return target_dir

    def mark_error(self, device_id: str, message: str) -> None:
        self._update_status(device_id, last_error=message)

    def load_status(self) -> SyncStatus:
        if not self.status_path.exists():
            return {"devices": {}}
        try:
            payload = json.loads(self.status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"devices": {}}
        return self._normalise_status(payload)

    # ------------------------------------------------------------------ 内部工具
    def _ensure_device(self, device_id: str) -> DeviceConfig:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise ConfigurationError(f"未找到 device_id={device_id} 对应的配置") from exc

    def _exec(self, device: DeviceConfig, adb_args: RunnerCommand) -> RunnerResult:
        command = ["adb", "-s", device.adb_serial, *adb_args]
        result = self._runner(command)
        if result.returncode != 0:
            self._update_status(
                device.device_id,
                last_error=result.stderr.strip() or "ADB command failed",
            )
            raise SyncCommandError(command, result.stderr)
        return result

    def _summarise_batch(self, batch_dir: Path) -> dict[str, Any]:
        style_dirs = [p for p in batch_dir.iterdir() if p.is_dir()]
        image_count = sum(len(list(style_dir.glob("*.jpg"))) for style_dir in style_dirs)

        summary: dict[str, Any] = {
            "summary": {
                "style_count": len(style_dirs),
                "image_count": image_count,
            }
        }

        manifest_path = batch_dir / "manifest.json"
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = None
            if isinstance(existing, MutableMapping):
                summary.update({key: value for key, value in existing.items() if key != "summary"})
        return summary

    def _prepare_pull_directory(self, device_id: str, timestamp: datetime) -> Path:
        dated = timestamp.strftime("%Y%m%d_%H%M%S")
        target = self.sync_root / f"device_{device_id}" / dated
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _update_status(
        self,
        device_id: str,
        *,
        last_push: datetime | None = None,
        last_pull: datetime | None = None,
        last_error: str | None = None,
        last_batch: str | None = None,
        last_pull_path: str | None = None,
        manifest: dict[str, Any] | None = None,
    ) -> None:
        status = self.load_status()
        device_status = status.setdefault("devices", {}).setdefault(device_id, {})

        if last_push is not None:
            device_status["last_push"] = last_push.replace(microsecond=0).isoformat()
        if last_pull is not None:
            device_status["last_pull"] = last_pull.replace(microsecond=0).isoformat()
        if last_error is not None:
            device_status["last_error"] = last_error
        if last_batch is not None:
            device_status["last_batch"] = last_batch
        if last_pull_path is not None:
            device_status["last_pull_path"] = last_pull_path
        if manifest is not None:
            device_status["last_manifest"] = manifest

        self.status_path.write_text(
            json.dumps(status, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _normalise_status(self, payload: Any) -> SyncStatus:
        status: SyncStatus = {"devices": {}}
        if not isinstance(payload, MutableMapping):
            return status

        raw_devices = payload.get("devices")
        if not isinstance(raw_devices, MutableMapping):
            return status

        for device_id, info in raw_devices.items():
            if not isinstance(device_id, str) or not isinstance(info, MutableMapping):
                continue
            device_status: DeviceStatus = {}

            for key in ("last_push", "last_pull", "last_batch", "last_pull_path"):
                value = info.get(key)
                if isinstance(value, str):
                    device_status[key] = value

            if "last_error" in info:
                err = info.get("last_error")
                if isinstance(err, str) or err is None:
                    device_status["last_error"] = err

            manifest = info.get("last_manifest")
            if isinstance(manifest, MutableMapping):
                device_status["last_manifest"] = dict(manifest)

            status["devices"][device_id] = device_status

        return status

    @staticmethod
    def _load_devices_from_yaml(config_path: Path) -> list[DeviceConfig]:
        if not config_path.exists():
            raise ConfigurationError(f"设备配置文件不存在: {config_path}")

        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:  # pragma: no cover - yaml errors are rare
            raise ConfigurationError(f"设备配置解析失败: {config_path}") from exc

        if raw is None:
            raise ConfigurationError(f"设备配置文件为空: {config_path}")

        if isinstance(raw, MutableMapping):
            devices_iterable = raw.get("devices")
        else:
            devices_iterable = raw

        if not isinstance(devices_iterable, Iterable):
            raise ConfigurationError("配置中缺少 devices 节点")

        devices: list[DeviceConfig] = []
        for item in devices_iterable:
            if not isinstance(item, MutableMapping):
                raise ConfigurationError("每个设备配置必须是键值对对象")

            try:
                device_id = cast(str, item["device_id"])
                serial = cast(str, item["adb_serial"])
            except KeyError as exc:
                raise ConfigurationError("设备配置缺少 device_id 或 adb_serial") from exc

            devices.append(
                DeviceConfig(
                    device_id=device_id,
                    adb_serial=serial,
                    remote_root=cast(str, item.get("remote_root", "/sdcard/XianyuTasks")),
                    todo_dir=cast(str, item.get("todo_dir", "Todo")),
                    done_dir=cast(str, item.get("done_dir", "Done")),
                )
            )

        return devices