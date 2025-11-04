from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, Sequence

__all__ = ["ScannedDevice", "DeviceScanner", "DeviceScannerError"]

RunnerCommand = Sequence[str]


@dataclass(slots=True)
class ScannedDevice:
    serial: str
    status: str
    product: str | None = None
    model: str | None = None
    device: str | None = None
    transport_id: str | None = None


@dataclass(slots=True)
class RunnerResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class DeviceScannerError(RuntimeError):
    pass


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


def _parse_line(line: str) -> ScannedDevice | None:
    line = line.strip()
    if not line or line.startswith("*") or line.lower().startswith("list of devices"):
        return None
    parts = line.split()
    if not parts:
        return None
    serial = parts[0]
    status = parts[1] if len(parts) > 1 else "unknown"
    meta: dict[str, str] = {}
    for token in parts[2:]:
        if ":" not in token:
            continue
        key, value = token.split(":", 1)
        meta[key] = value
    return ScannedDevice(
        serial=serial,
        status=status,
        product=meta.get("product"),
        model=meta.get("model"),
        device=meta.get("device"),
        transport_id=meta.get("transport_id"),
    )


class DeviceScanner:
    def __init__(
        self,
        adb_path: str = "adb",
        runner: Callable[[RunnerCommand], RunnerResult] | None = None,
    ) -> None:
        self.adb_path = adb_path
        self._runner = runner or _default_runner

    def scan(self) -> list[ScannedDevice]:
        result = self._runner([self.adb_path, "devices", "-l"])
        if result.returncode != 0:
            raise DeviceScannerError(result.stderr.strip() or "adb devices 调用失败")
        devices: list[ScannedDevice] = []
        for line in result.stdout.splitlines():
            parsed = _parse_line(line)
            if parsed is not None:
                devices.append(parsed)
        return devices
