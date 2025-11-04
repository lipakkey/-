from __future__ import annotations

from PySide6.QtWidgets import QWidget

__all__ = ["add_panel_header"]


def add_panel_header(widget: QWidget, color: str) -> None:
    """Apply a simple colored border to panel widgets."""
    widget.setProperty("panelAccent", color)
    widget.setStyleSheet(
        """
        QWidget[panelAccent] {
            border: 1px solid palette(midlight);
            border-top: 4px solid %s;
            border-radius: 4px;
            background: palette(Base);
        }
        """
        % color
    )
