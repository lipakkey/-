from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable

from app.desktop.core.background import Worker
from app.desktop.core.logger import get_logger
from app.desktop.models.task_bundle import TaskBundle
from app.desktop.services.device_scanner import DeviceScanner, ScannedDevice
from app.desktop.services.sync_service import SyncService

logger = get_logger("sync.controller")


class SyncController:
    def __init__(
        self,
        presenter,
        service: SyncService | None = None,
        scanner: DeviceScanner | None = None,
    ) -> None:
        self.presenter = presenter
        self.sync_service = service or SyncService(Path.cwd())
        self.device_scanner = scanner or DeviceScanner()
        self._pending: dict[str, list[TaskBundle]] = {}

    # ------------------------------------------------------------------ 队列管理
    def register_batches(self, bundles: Iterable[TaskBundle]) -> dict[str, int]:
        for bundle in bundles:
            device_queue = self._pending.setdefault(bundle.device_id, [])
            device_queue.append(bundle)
            logger.info("登记待推送批次: %s -> %s", bundle.device_id, bundle.bundle_path)
            self.presenter.on_message(f"{bundle.device_id} 待推送批次 +{bundle.style_count}")
        snapshot = self._pending_snapshot()
        self._write_queue_file(snapshot)
        self.presenter.on_queue_update(snapshot)
        return snapshot

    def _pending_snapshot(self) -> dict[str, int]:
        return {device: len(bundles) for device, bundles in self._pending.items()}

    def _write_queue_file(self, snapshot: dict[str, int]) -> None:
        pending_file = self.sync_service.sync_root / "queue.json"
        pending_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    def configured_devices(self):
        return self.sync_service.list_devices()

    def current_status(self) -> dict:
        return self.sync_service.load_status()

    def scan_devices(self) -> list[ScannedDevice]:
        devices = self.device_scanner.scan()
        return devices

    # ------------------------------------------------------------------ 执行操作
    def push_all(self) -> None:
        for device in self.sync_service.list_devices():
            bundles = self._pending.get(device.device_id, [])
            if not bundles:
                self.presenter.on_message(f"{device.device_id} 暂无待推送任务")
                continue
            for bundle in list(bundles):
                staged_path = self._stage_bundle(device.device_id, bundle)
                worker = Worker(
                    self.sync_service.push_batch,
                    args=(device.device_id, staged_path),
                )
                worker.finished.connect(
                    lambda _=None, d=device.device_id, b=bundle: self._on_push_success(d, b)
                )  # type: ignore[arg-type]
                worker.failed.connect(self.presenter.on_message)  # type: ignore[arg-type]
                worker.start()

    def pull_all(self) -> None:
        for device in self.sync_service.list_devices():
            worker = Worker(
                self.sync_service.pull_logs,
                args=(device.device_id,),
            )
            worker.finished.connect(
                lambda path, d=device.device_id: self.presenter.on_message(f"已拉取 {d}: {path}")
            )  # type: ignore[arg-type]
            worker.failed.connect(self.presenter.on_message)  # type: ignore[arg-type]
            worker.start()

    # ------------------------------------------------------------------ 回调 & 工具
    def _stage_bundle(self, device_id: str, bundle: TaskBundle) -> Path:
        pending_dir = self.sync_service.sync_root / "pending" / device_id
        pending_dir.mkdir(parents=True, exist_ok=True)
        staged = pending_dir / bundle.bundle_path.name
        if staged.exists():
            shutil.rmtree(staged)
        shutil.copytree(bundle.bundle_path, staged)
        logger.info("批次已拷贝到待推送目录: %s", staged)
        return staged

    def _on_push_success(self, device_id: str, bundle: TaskBundle) -> None:
        bundles = self._pending.get(device_id, [])
        if bundle in bundles:
            bundles.remove(bundle)
        self.presenter.on_message(f"{device_id} 推送完成：{bundle.bundle_path}")
        snapshot = self._pending_snapshot()
        self._write_queue_file(snapshot)
        self.presenter.on_queue_update(snapshot)

    def load_status(self) -> dict[str, dict]:
        return self.sync_service.load_status()
