from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.desktop.ui.widgets import add_panel_header
from app.desktop.ui.style import ACCENT
from app.desktop.viewmodels.sync_viewmodel import SyncViewModel


class SyncPanel(QWidget):
    """同步面板：负责与安卓设备进行推送和日志拉取。"""

    def __init__(self, status_bar=None, viewmodel: SyncViewModel | None = None) -> None:
        super().__init__()
        self.status_bar = status_bar
        self.viewmodel = viewmodel or SyncViewModel()
        self.queue_snapshot: dict[str, int] = {}
        self._init_ui()
        self._wire_signals()
        add_panel_header(self, ACCENT)
        self.viewmodel.refresh_status()

    def _wire_signals(self) -> None:
        self.viewmodel.sync_message.connect(self._notify)
        self.viewmodel.status_changed.connect(self._update_status_table)
        self.viewmodel.queue_changed.connect(self._update_queue)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_device_box())
        layout.addWidget(self._build_queue_box())
        layout.addStretch(1)

    def _build_device_box(self) -> QGroupBox:
        box = QGroupBox("设备概览")
        v = QVBoxLayout(box)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "设备ID",
            "待推送",
            "最后批次",
            "最后推送",
            "最后拉取",
            "状态",
        ])

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新状态")
        self.push_all = QPushButton("推送全部")
        self.pull_all = QPushButton("拉取全部")
        self.refresh_btn.clicked.connect(self.viewmodel.refresh_status)
        self.push_all.clicked.connect(self.viewmodel.push_all_devices)
        self.pull_all.clicked.connect(self.viewmodel.pull_all_devices)

        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.push_all)
        btn_row.addWidget(self.pull_all)
        btn_row.addStretch(1)

        v.addWidget(self.table)
        v.addLayout(btn_row)
        return box

    def _build_queue_box(self) -> QGroupBox:
        box = QGroupBox("待推送批次")
        self.queue_list = QListWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(self.queue_list)
        return box

    def register_bundles(self, bundles) -> None:
        self.viewmodel.register_bundles(bundles)

    def _update_status_table(self, status: dict) -> None:
        devices = status.get("devices", {}) if isinstance(status, dict) else {}
        self.table.setRowCount(len(devices))
        for row, (device_id, info) in enumerate(devices.items()):
            pending = str(self.queue_snapshot.get(device_id, 0))
            last_batch = info.get("last_batch", "-") if isinstance(info, dict) else "-"
            last_push = info.get("last_push", "-") if isinstance(info, dict) else "-"
            last_pull = info.get("last_pull", "-") if isinstance(info, dict) else "-"
            status_text = info.get("last_error") if isinstance(info, dict) else None
            if status_text:
                final_status = f"异常: {status_text}"
            else:
                final_status = "正常"
            values = [device_id, pending, last_batch or "-", last_push or "-", last_pull or "-", final_status]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def _update_queue(self, snapshot: dict) -> None:
        self.queue_snapshot = snapshot or {}
        self.queue_list.clear()
        for device_id, count in self.queue_snapshot.items():
            item = QListWidgetItem(f"{device_id}: 待推送 {count}")
            self.queue_list.addItem(item)
        self.viewmodel.refresh_status()

    def _notify(self, text: str) -> None:
        if self.status_bar:
            self.status_bar.showMessage(text, 3000)
