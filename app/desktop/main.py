from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("电子衣柜 - 桌面端")
        self.resize(1280, 760)
        placeholder = QLabel("桌面端 UI 正在建设中…", alignment=0x0084)
        self.setCentralWidget(placeholder)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    main()
