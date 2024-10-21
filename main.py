from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QLayout,
    QBoxLayout,
    QVBoxLayout,
    QPushButton,
)
from ftplib import FTP

import sys
import os
import ctypes

from constants import app_title
from ftp import ReusableFTP
from login import LoginFTPWidget
from server import ServerWidget
from utils import delete_items_of_layout

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
        self.login_ui = None
        self.server_ui = None
        self.central_widget = QStackedWidget()

        self.setCentralWidget(self.central_widget)
        self.start_login_ui()

    def start_login_ui(self):
        self.login_ui = LoginFTPWidget(self)
        self.central_widget.addWidget(self.login_ui)
        self.central_widget.setCurrentWidget(self.login_ui)

    def start_server_ui(self):
        self.server_ui = ServerWidget(self)
        self.central_widget.addWidget(self.server_ui)
        self.central_widget.setCurrentWidget(self.server_ui)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
