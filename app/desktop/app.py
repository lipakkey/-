from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.desktop.ui.main_window import MainWindow


def run_app() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    run_app()
