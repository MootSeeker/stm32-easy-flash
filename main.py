"""Entry point for STM32 Easy Flash GUI application."""

import sys

from PySide6.QtWidgets import QApplication

from stm32_easy_flash.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
