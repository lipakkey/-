from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
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
    """同步面板：负责批次推送、日志显示与设备扫描。"""

    LOG_HEADERS = ["时间", "消息", "级别"]

    def __init__(self, status_bar=None, viewmodel: SyncViewModel | None = None) -> None:
        super().__init__()
        self.status_bar = status_bar
        self.viewmodel = viewmodel or SyncViewModel()
        self.queue_snapshot: dict[str, int] = {}
        self.scan_status: dict[str, str] = {}
        self.log_entries: list[dict[str, str]] = []
        self._init_ui()
        self._wire_signals()
        add_panel_header(self, ACCENT)
        self.viewmodel.refresh_status()

    # ------------------------------------------------------------------ setup
    def _wire_signals(self) -> None:
        self.viewmodel.sync_message.connect(self._handle_message)
        self.viewmodel.status_changed.connect(self._update_status_table)
        self.viewmodel.queue_changed.connect(self._update_queue)
        self.viewmodel.scan_completed.connect(self._on_scan_completed)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_device_box())
        layout.addWidget(self._build_queue_box())
        layout.addWidget(self._build_log_box())
        layout.addStretch(1)

    def _build_device_box(self) -> QGroupBox:
        box = QGroupBox("设备面板")
        vbox = QVBoxLayout(box)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "设备ID",
                "ADB 序列号",
                "待推送",
                "最新批次",
                "最后推送",
                "最后拉取",
                "扫描状态",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("扫描设备")
        self.refresh_btn = QPushButton("刷新状态")
        self.push_all_btn = QPushButton("推送全部")
        self.pull_all_btn = QPushButton("拉取全部")

        self.scan_btn.clicked.connect(self.viewmodel.scan_devices)
        self.refresh_btn.clicked.connect(self.viewmodel.refresh_status)
        self.push_all_btn.clicked.connect(self.viewmodel.push_all_devices)
        self.pull_all_btn.clicked.connect(self.viewmodel.pull_all_devices)

        for btn in (self.scan_btn, self.refresh_btn, self.push_all_btn, self.pull_all_btn):
            btn_row.addWidget(btn)
        btn_row.addStretch(1)

        vbox.addWidget(self.table)
        vbox.addLayout(btn_row)
        return box

    def _build_queue_box(self) -> QGroupBox:
        box = QGroupBox("待推送队列")
        vbox = QVBoxLayout(box)
        self.queue_list = QListWidget()
        vbox.addWidget(self.queue_list)
        return box

    def _build_log_box(self) -> QGroupBox:
        box = QGroupBox("最近操作日志")
        vbox = QVBoxLayout(box)

        filter_row = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "仅错误"])
        self.filter_combo.currentIndexChanged.connect(self._apply_log_filter)

        self.export_btn = QPushButton("导出 CSV")
        self.clear_btn = QPushButton("清除日志")
        self.export_btn.clicked.connect(self._export_logs)
        self.clear_btn.clicked.connect(self._clear_logs)

        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch(1)
        filter_row.addWidget(self.export_btn)
        filter_row.addWidget(self.clear_btn)

        self.log_table = QTableWidget(0, len(self.LOG_HEADERS))
        self.log_table.setHorizontalHeaderLabels(self.LOG_HEADERS)
        self.log_table.horizontalHeader().setStretchLastSection(True)

        vbox.addLayout(filter_row)
        vbox.addWidget(self.log_table)
        return box

    # ------------------------------------------------------------------ queue & devices
    def register_bundles(self, bundles: Iterable) -> None:  # pragma: no cover - presenter path
        self.viewmodel.register_bundles(bundles)

    def _update_status_table(self, status: dict) -> None:
        status_devices = status.get("devices", {}) if isinstance(status, dict) else {}
        configured = self.viewmodel.configured_devices()
        self.table.setRowCount(len(configured))
        for row, cfg in enumerate(configured):
            device_status = status_devices.get(cfg.device_id, {})
            pending = str(self.queue_snapshot.get(cfg.device_id, 0))
            last_batch = device_status.get("last_batch", "-") if isinstance(device_status, dict) else "-"
            last_push = device_status.get("last_push", "-") if isinstance(device_status, dict) else "-"
            last_pull = device_status.get("last_pull", "-") if isinstance(device_status, dict) else "-"
            last_error = device_status.get("last_error") if isinstance(device_status, dict) else None
            scan_state = self.scan_status.get(cfg.adb_serial, "未扫描")
            final_status = f"异常: {last_error}" if last_error else scan_state

            values = [
                cfg.device_id,
                cfg.adb_serial,
                pending,
                last_batch or "-",
                last_push or "-",
                last_pull or "-",
                final_status,
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def _update_queue(self, snapshot: dict) -> None:
        self.queue_snapshot = snapshot or {}
        self.queue_list.clear()
        if isinstance(snapshot, dict):
            for device_id, count in snapshot.items():
                item = QListWidgetItem(f"{device_id}: 待推送 {count}")
                self.queue_list.addItem(item)
        if self.queue_list.count():
            self.queue_list.setCurrentRow(0)
            self._on_queue_selected()
        else:
            self.pipeline_panel_ref().show_batch_details("")

    def _on_scan_completed(self, devices) -> None:
        if isinstance(devices, list):
            self.scan_status = {
                getattr(device, "serial", ""): getattr(device, "status", "")
                for device in devices
                if getattr(device, "serial", "")
            }
            self._handle_message(f"已扫描 {len(self.scan_status)} 台设备")
        else:
            self.scan_status = {}
            self._handle_message("未扫描到设备")
        self.viewmodel.refresh_status()

    def _on_queue_selected(self) -> None:
        item = self.queue_list.currentItem()
        if item is not None:
            self.pipeline_panel_ref().show_batch_details(item.text())

    # ------------------------------------------------------------------ logging helpers
    def _handle_message(self, text: str) -> None:
        if self.status_bar:
            self.status_bar.showMessage(text, 3000)
        self._append_log(text)

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = "error" if self._is_error_message(message) else "info"
        record = {"time": timestamp, "message": message, "level": level}
        self.log_entries.append(record)
        self._apply_log_filter()

    def _apply_log_filter(self) -> None:
        show_errors_only = self.filter_combo.currentIndex() == 1
        self.log_table.setRowCount(0)
        for record in self.log_entries:
            if show_errors_only and record["level"] != "error":
                continue
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            self.log_table.setItem(row, 0, QTableWidgetItem(record["time"]))
            self.log_table.setItem(row, 1, QTableWidgetItem(record["message"]))
            self.log_table.setItem(row, 2, QTableWidgetItem(record["level"]))
        self.log_table.scrollToBottom()

    def _clear_logs(self) -> None:
        self.log_entries.clear()
        self.log_table.setRowCount(0)

    def _export_logs(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "导出日志", str(Path.cwd()), "CSV (*.csv)")
        if not filename:
            return
        rows = []
        show_errors_only = self.filter_combo.currentIndex() == 1
        for record in self.log_entries:
            if show_errors_only and record["level"] != "error":
                continue
            rows.append(record)
        lines = ["时间,消息,级别"]
        for record in rows:
            safe_msg = record["message"].replace('"', '""')
            lines.append(f"{record['time']},\"{safe_msg}\",{record['level']}")
        Path(filename).write_text("\n".join(lines), encoding="utf-8")
        self._handle_message(f"日志已导出到 {filename}")

    @staticmethod
    def _is_error_message(message: str) -> bool:
        lower = message.lower()
        return any(keyword in lower for keyword in ("error", "异常", "failed", "fail"))

    def pipeline_panel_ref(self) -> "PipelinePanel":
        # type: ignore[return-value] - main window will monkey patch this attribute
        return getattr(self, "_pipeline_panel_ref", None)

    def set_pipeline_panel(self, pipeline_panel) -> None:
        self._pipeline_panel_ref = pipeline_panel

