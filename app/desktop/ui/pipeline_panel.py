from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QListView,
    QPushButton,
    QScrollArea,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QTextEdit,
)

from app.desktop.models.pipeline_config import PipelineConfig
from app.desktop.ui.widgets import add_panel_header
from app.desktop.ui.style import PRIMARY
from app.desktop.viewmodels.pipeline_viewmodel import PipelineViewModel


class PipelinePanel(QWidget):
    """中央厨房控制面板：配置输入、触发生成、查看进度。"""

    def __init__(
        self,
        status_bar=None,
        viewmodel: PipelineViewModel | None = None,
    ) -> None:
        super().__init__()
        self.status_bar = status_bar
        self.viewmodel = viewmodel or PipelineViewModel()
        self._init_ui()
        self._wire_signals()
        add_panel_header(self, PRIMARY)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(self._build_config_box())
        container_layout.addWidget(self._build_task_box())
        container_layout.addWidget(self._build_control_box())
        container_layout.addStretch(1)
        scroll.setWidget(container)

        layout.addWidget(scroll)

    def _wire_signals(self) -> None:
        self.viewmodel.pipeline_progress.connect(self._on_progress)
        self.viewmodel.pipeline_finished.connect(self._on_finished)
        self.viewmodel.pipeline_failed.connect(self._on_failed)

    # --- sections
    def _build_config_box(self) -> QGroupBox:
        box = QGroupBox("任务配置")
        form = QFormLayout(box)

        self.input_edit = QLineEdit(str(Path("data/Input_Raw")))
        browse_input = QPushButton("浏览")
        browse_input.clicked.connect(lambda: self._select_dir(self.input_edit))
        form.addRow("素材目录", self._combine(self.input_edit, browse_input))

        self.output_edit = QLineEdit(str(Path("data/Output")))
        browse_output = QPushButton("浏览")
        browse_output.clicked.connect(lambda: self._select_dir(self.output_edit))
        form.addRow("输出目录", self._combine(self.output_edit, browse_output))

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(10, 9999)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(299.00)
        form.addRow("统一价格", self.price_spin)

        self.template_box = QLineEdit("tee")
        form.addRow("文案模板", self.template_box)

        self.device_list = QListWidget()
        for device in ("phone1", "phone2", "phone3"):
            item = QListWidgetItem(device)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.device_list.addItem(item)
        self.device_list.setViewMode(QListView.ViewMode.ListMode)
        form.addRow("分发设备", self.device_list)

        return box

    def _build_task_box(self) -> QGroupBox:
        box = QGroupBox("执行进度")
        layout = QVBoxLayout(box)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        self.current_label = QLabel("等待开始...")
        layout.addWidget(self.current_label)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        return box

    def _build_control_box(self) -> QGroupBox:
        box = QGroupBox("操作")
        layout = QHBoxLayout(box)

        self.start_btn = QPushButton("开始生成")
        self.pause_btn = QPushButton("暂停")
        self.stop_btn = QPushButton("终止")

        self.start_btn.clicked.connect(self._on_start)
        self.pause_btn.clicked.connect(lambda: self._append_log("暂停功能待实现"))
        self.stop_btn.clicked.connect(lambda: self._append_log("终止功能待实现"))

        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch(1)
        return box

    # --- helpers
    def _combine(self, field: QWidget, button: QPushButton) -> QWidget:
        wrapper = QWidget()
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(field)
        h.addWidget(button)
        return wrapper

    def _select_dir(self, target: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择目录", target.text())
        if path:
            target.setText(path)

    def _append_log(self, text: str) -> None:
        self.log_view.append(text)
        if self.status_bar:
            self.status_bar.showMessage(text, 5000)

    def _checked_devices(self) -> tuple[str, ...]:
        devices: list[str] = []
        for index in range(self.device_list.count()):
            item = self.device_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                devices.append(item.text())
        return tuple(devices)

    def _on_start(self) -> None:
        config = PipelineConfig(
            input_root=Path(self.input_edit.text()),
            output_root=Path(self.output_edit.text()),
            devices=self._checked_devices(),
            price=self.price_spin.value(),
        )
        self.viewmodel.update_config(config)
        self.start_btn.setEnabled(False)
        self.progress.setValue(0)
        self._append_log("开始生成任务...")
        self.viewmodel.run_pipeline_async()

    def _on_progress(self, pct: int, message: str) -> None:
        self.progress.setValue(pct)
        self.current_label.setText(message)
        self._append_log(message)

    def _on_finished(self, bundles) -> None:
        self.start_btn.setEnabled(True)
        self.progress.setValue(100)
        self._append_log("中央厨房任务完成")
        self.current_label.setText("生成完成")

    def _on_failed(self, message: str) -> None:
        self.start_btn.setEnabled(True)
        self._append_log(f"错误：{message}")
        self.current_label.setText(message)
