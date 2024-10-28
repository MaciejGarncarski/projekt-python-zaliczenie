from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
)

import sys
import os
import ctypes

from constants import app_title
from ftp import ftp_client
from login import LoginFTPWidget
from server import ServerWidget

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
        self.setFixedSize(400, 400)
        self.login_ui = LoginFTPWidget(
            self, start_server_ui=self.start_server_ui, main_window=self
        )
        self.central_widget.addWidget(self.login_ui)
        self.central_widget.setCurrentWidget(self.login_ui)

    def start_server_ui(self):
        self.setFixedSize(600, 500)
        self.server_ui = ServerWidget(self, start_login_ui=self.start_login_ui)
        self.central_widget.addWidget(self.server_ui)
        self.central_widget.setCurrentWidget(self.server_ui)


def excepthook(exc_type, exc_value, exc_tb):
    ftp_client.reconnect()
    QtWidgets.QApplication.quit()


sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
