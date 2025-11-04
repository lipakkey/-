from __future__ import annotations

from PySide6.QtGui import QColor, QPalette

PRIMARY = "#1C5D99"
ACCENT = "#FF9F1C"
SUCCESS = "#2EC4B6"
DANGER = "#E71D36"
BACKGROUND = "#F4F7FB"
PANEL_BG = "#FFFFFF"
TEXT_TITLE = "#1F2933"
TEXT_BODY = "#4B5563"


def apply_global_theme(app) -> None:
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor(PANEL_BG))
    palette.setColor(QPalette.ColorRole.Button, QColor(PRIMARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_BODY))
    app.setPalette(palette)

    app.setStyleSheet(
        f"""
        QWidget {{
            font-family: 'Source Han Sans SC', 'Microsoft YaHei', 'Inter';
            font-size: 13px;
            color: {TEXT_BODY};
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid #D8DEE9;
            border-radius: 6px;
            margin-top: 12px;
            padding: 12px;
        }}
        QPushButton {{
            background: {PRIMARY};
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
        }}
        QPushButton:disabled {{ background: #9CA3AF; color: #ECECEC; }}
        QPushButton:hover {{ background: #2170BF; }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            border: 1px solid #CBD5E0;
            border-radius: 4px;
            padding: 4px 6px;
            background: white;
        }}
        QListWidget {{ border: 1px solid #E5E7EB; }}
        QProgressBar {{
            border: 1px solid #CBD5E0;
            border-radius: 6px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {SUCCESS};
            border-radius: 6px;
        }}
        QTableWidget {{
            gridline-color: #E5E7EB;
            selection-background-color: {PRIMARY};
            selection-color: white;
        }}
        """
    )
