from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.desktop.ui.pipeline_panel import PipelinePanel
from app.desktop.ui.sync_panel import SyncPanel
from app.desktop.ui.report_panel import ReportPanel


class MainWindow(QMainWindow):
    """主窗口：中央厨房、同步控制、报告浏览的容器。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("电子衣柜 1.0 - 桌面控制台")
        self.resize(1440, 900)

        self._init_menu()
        self._init_status_bar()
        self._init_layout()
        self._wire_cross_panel_events()
        self._populate_initial_devices()

    def _init_menu(self) -> None:
        menu = QMenuBar(self)
        file_menu = menu.addMenu("文件")
        file_menu.addAction("导出配置")
        file_menu.addAction("打开日志目录")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        view_menu = menu.addMenu("视图")
        view_menu.addAction("重置布局")

        help_menu = menu.addMenu("帮助")
        help_menu.addAction("查看使用手册")
        self.setMenuBar(menu)

    def _init_status_bar(self) -> None:
        status = QStatusBar(self)
        status.showMessage("欢迎使用电子衣柜控制台")
        self.setStatusBar(status)

    def _init_layout(self) -> None:
        splitter = QSplitter()

        self.nav_panel = QWidget()
        nav_layout = QVBoxLayout(self.nav_panel)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(12)

        self.device_label = QLabel("目标设备")
        self.device_combo = QComboBox()
        self.scan_nav_btn = QPushButton("扫描设备")
        self.refresh_nav_btn = QPushButton("刷新状态")

        nav_layout.addWidget(self.device_label)
        nav_layout.addWidget(self.device_combo)
        nav_layout.addWidget(self.scan_nav_btn)
        nav_layout.addWidget(self.refresh_nav_btn)

        self.queue_label = QLabel("待推送批次")
        self.queue_list = QListWidget()
        nav_layout.addWidget(self.queue_label)
        nav_layout.addWidget(self.queue_list, stretch=1)

        self.tabs = QTabWidget()
        self.pipeline_panel = PipelinePanel(self.statusBar())
        self.sync_panel = SyncPanel(self.statusBar())
        self.report_panel = ReportPanel(self.statusBar())
        self.tabs.addTab(self.pipeline_panel, "中央厨房")
        self.tabs.addTab(self.sync_panel, "同步")
        self.tabs.addTab(self.report_panel, "报告")

        splitter.addWidget(self.nav_panel)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        self.setCentralWidget(splitter)

    def _wire_cross_panel_events(self) -> None:
        self.pipeline_panel.viewmodel.pipeline_finished.connect(self.sync_panel.register_bundles)
        self.sync_panel.viewmodel.queue_changed.connect(self._update_nav_queue)
        self.sync_panel.viewmodel.scan_completed.connect(self._update_nav_devices)
        self.scan_nav_btn.clicked.connect(self.sync_panel.viewmodel.scan_devices)
        self.refresh_nav_btn.clicked.connect(self.sync_panel.viewmodel.refresh_status)

    def _populate_initial_devices(self) -> None:
        devices = self.sync_panel.viewmodel.configured_devices()
        self.device_combo.clear()
        for cfg in devices:
            self.device_combo.addItem(f"{cfg.device_id} ({cfg.adb_serial})", cfg.device_id)

    def _update_nav_devices(self, devices) -> None:
        self.device_combo.clear()
        if isinstance(devices, list) and devices:
            for dev in devices:
                serial = getattr(dev, "serial", "?")
                status = getattr(dev, "status", "unknown")
                self.device_combo.addItem(f"{serial} [{status}]", serial)
        else:
            configured = self.sync_panel.viewmodel.configured_devices()
            for cfg in configured:
                self.device_combo.addItem(f"{cfg.device_id} ({cfg.adb_serial})", cfg.device_id)

    def _update_nav_queue(self, snapshot: dict) -> None:
        self.queue_list.clear()
        if isinstance(snapshot, dict):
            for device_id, count in snapshot.items():
                item = QListWidgetItem(f"{device_id}: 待推送 {count}")
                self.queue_list.addItem(item)

