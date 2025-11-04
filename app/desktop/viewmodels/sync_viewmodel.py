from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.desktop.controllers.sync_controller import SyncController
from app.desktop.services.device_scanner import ScannedDevice
from app.desktop.services.sync_service import DeviceConfig


class SyncViewModel(QObject):
    sync_message = Signal(str)
    status_changed = Signal(object)
    queue_changed = Signal(object)
    scan_completed = Signal(object)

    def __init__(self, controller: SyncController | None = None) -> None:
        super().__init__()
        self.controller = controller or SyncController(self)
        self._last_scan: list[ScannedDevice] = []

    def register_bundles(self, bundles) -> None:
        queued = self.controller.register_batches(bundles)
        self.queue_changed.emit(queued)

    def push_all_devices(self) -> None:
        self.controller.push_all()

    def pull_all_devices(self) -> None:
        self.controller.pull_all()

    def refresh_status(self) -> None:
        status = self.controller.load_status()
        self.status_changed.emit(status)

    def scan_devices(self) -> None:
        try:
            devices = self.controller.scan_devices()
        except Exception as exc:  # pragma: no cover - GUI only
            self.sync_message.emit(str(exc))
            return
        self._last_scan = devices
        self.scan_completed.emit(devices)

    def configured_devices(self) -> list[DeviceConfig]:
        return self.controller.configured_devices()

    def last_scanned_devices(self) -> list[ScannedDevice]:
        return list(self._last_scan)

    def on_message(self, text: str) -> None:
        self.sync_message.emit(text)

    def on_queue_update(self, queued) -> None:
        self.queue_changed.emit(queued)
