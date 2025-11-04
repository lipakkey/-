from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.desktop.controllers.sync_controller import SyncController


class SyncViewModel(QObject):
    sync_message = Signal(str)
    status_changed = Signal(object)
    queue_changed = Signal(object)

    def __init__(self, controller: SyncController | None = None) -> None:
        super().__init__()
        self.controller = controller or SyncController(self)

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

    def on_message(self, text: str) -> None:
        self.sync_message.emit(text)

    def on_queue_update(self, queued) -> None:
        self.queue_changed.emit(queued)
