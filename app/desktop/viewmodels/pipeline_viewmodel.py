from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.desktop.controllers.pipeline_controller import PipelineController


class PipelineViewModel(QObject):
    pipeline_started = Signal()
    pipeline_finished = Signal()

    def __init__(self, controller: PipelineController | None = None) -> None:
        super().__init__()
        self.controller = controller or PipelineController(self)

    def run_pipeline_async(self) -> None:
        self.pipeline_started.emit()
        self.controller.run_async()
