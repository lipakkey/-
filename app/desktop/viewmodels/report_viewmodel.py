from __future__ import annotations

from PySide6.QtCore import QObject

from app.desktop.controllers.report_controller import ReportController


class ReportViewModel(QObject):
    def __init__(self, controller: ReportController | None = None) -> None:
        super().__init__()
        self.controller = controller or ReportController()

    def list_reports(self):
        return self.controller.list_reports()
