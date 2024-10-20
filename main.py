from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow

import sys
import os
import ctypes

from constants import app_title
from login import LoginFTPWidget

# ustawia ikonkę aplikacji na systemie Windows,
# poprzez ustawienie własnego identyfikatora aplikacji
if os.name == "nt":
    myappid = "maciejgarncarski.projektFTP.WdP.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(app_title)
        pixmap = QPixmap()
        pixmap.loadFromData(Path("logo.png").read_bytes())
        app_icon = QIcon(pixmap)
        self.setWindowIcon(app_icon)
        self.setFixedSize(400, 400)
        self.login_ui = LoginFTPWidget()
        self.start_login_ui()

    def start_login_ui(self):
        self.login_ui.init_ui(self)
        self.show()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
