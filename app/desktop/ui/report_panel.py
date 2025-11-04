from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.desktop.ui.widgets import add_panel_header
from app.desktop.ui.style import SUCCESS
from app.desktop.viewmodels.report_viewmodel import ReportViewModel


class ReportPanel(QWidget):
    """展示生成结果及安卓回传报告。"""

    def __init__(self, status_bar=None, viewmodel: ReportViewModel | None = None) -> None:
        super().__init__()
        self.status_bar = status_bar
        self.viewmodel = viewmodel or ReportViewModel()
        self._init_ui()
        add_panel_header(self, SUCCESS)
        self.refresh_reports()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_filter_box())
        layout.addWidget(self._build_report_table())
        layout.addWidget(self._build_failure_box())
        layout.addStretch(1)

    def _build_filter_box(self) -> QGroupBox:
        box = QGroupBox("筛选")
        layout = QHBoxLayout(box)

        self.device_filter = QComboBox()
        self.device_filter.addItems(["全部设备", "phone1", "phone2", "phone3"])
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "有失败", "全成功"])
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索款号/关键字")
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_reports)

        layout.addWidget(QLabel("设备"))
        layout.addWidget(self.device_filter)
        layout.addWidget(QLabel("状态"))
        layout.addWidget(self.status_filter)
        layout.addWidget(self.search_box)
        layout.addWidget(self.refresh_btn)
        return box

    def _build_report_table(self) -> QGroupBox:
        box = QGroupBox("报告列表")
        v = QVBoxLayout(box)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "时间",
            "设备",
            "总数",
            "成功",
            "失败数",
            "备注",
        ])
        self.table.cellClicked.connect(self._on_row_selected)
        v.addWidget(self.table)
        return box

    def _build_failure_box(self) -> QGroupBox:
        box = QGroupBox("失败明细 / 截图")
        layout = QVBoxLayout(box)
        self.fail_list = QListWidget()
        layout.addWidget(self.fail_list)
        return box

    def refresh_reports(self) -> None:
        entries = list(self.viewmodel.list_reports())
        device_filter = self.device_filter.currentText()
        status_filter = self.status_filter.currentText()
        keyword = self.search_box.text().strip().lower()

        filtered = []
        for entry in entries:
            if device_filter != "全部设备" and entry.device_id != device_filter:
                continue
            has_failure = bool(entry.failures)
            if status_filter == "有失败" and not has_failure:
                continue
            if status_filter == "全成功" and has_failure:
                continue
            if keyword and keyword not in entry.title.lower():
                continue
            filtered.append(entry)

        self.table.setRowCount(len(filtered))
        for row, entry in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(entry.created_at))
            self.table.setItem(row, 1, QTableWidgetItem(entry.device_id or "-"))
            self.table.setItem(row, 2, QTableWidgetItem(str(entry.total)))
            self.table.setItem(row, 3, QTableWidgetItem(str(entry.success)))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(entry.failures))))
            remark = entry.failures[0] if entry.failures else "-"
            self.table.setItem(row, 5, QTableWidgetItem(remark))
            self.table.setRowHeight(row, 28)
        self._current_entries = filtered
        self.fail_list.clear()
        if self.status_bar:
            self.status_bar.showMessage(f"共加载 {len(filtered)} 条报告", 3000)

    def _on_row_selected(self, row: int, column: int) -> None:
        if not hasattr(self, "_current_entries"):
            return
        if row >= len(self._current_entries):
            return
        entry = self._current_entries[row]
        self.fail_list.clear()
        if entry.failures:
            self.fail_list.addItem("失败明细：")
            for failure in entry.failures:
                self.fail_list.addItem(f" - {failure}")
        else:
            self.fail_list.addItem("无失败记录")
        if entry.screenshots:
            self.fail_list.addItem("截图：")
            for shot in entry.screenshots:
                item = QListWidgetItem(str(shot))
                item.setData(Qt.ItemDataRole.UserRole, shot)
                self.fail_list.addItem(item)
