from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QMenuBar, QStatusBar

from app.desktop.ui.pipeline_panel import PipelinePanel
from app.desktop.ui.sync_panel import SyncPanel
from app.desktop.ui.report_panel import ReportPanel


class MainWindow(QMainWindow):
    """主窗口，包含中央厨房、同步、报告三个面板。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("电子衣柜 1.0 - 桌面控制台")
        self.resize(1440, 900)

        self._init_menu()
        self._init_status_bar()
        self._init_layout()
        self._wire_cross_panel_events()

    def _init_menu(self) -> None:
        menu = QMenuBar(self)
        file_menu = menu.addMenu("文件")
        file_menu.addAction("打开配置")
        file_menu.addAction("导出日志")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        view_menu = menu.addMenu("视图")
        view_menu.addAction("重置布局")
        help_menu = menu.addMenu("帮助")
        help_menu.addAction("查看操作手册")
        self.setMenuBar(menu)

    def _init_status_bar(self) -> None:
        status = QStatusBar(self)
        status.showMessage("就绪")
        self.setStatusBar(status)

    def _init_layout(self) -> None:
        splitter = QSplitter()
        self.pipeline_panel = PipelinePanel(self.statusBar())
        self.sync_panel = SyncPanel(self.statusBar())
        self.report_panel = ReportPanel(self.statusBar())

        splitter.addWidget(self.pipeline_panel)
        splitter.addWidget(self.sync_panel)
        splitter.addWidget(self.report_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 3)
        self.setCentralWidget(splitter)

    def _wire_cross_panel_events(self) -> None:
        self.pipeline_panel.viewmodel.pipeline_finished.connect(self.sync_panel.register_bundles)
