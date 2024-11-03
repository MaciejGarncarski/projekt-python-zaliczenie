from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
)

import sys
from os import name, path
import ctypes

from constants import app_title
from dialog import ConfirmationBox
from ftp import ftp_client
from login import LoginFTPWidget
from server import ServerWidget


# Ustawia identyfikator aplikacji na systemie Windows,
# co pozwala na ustawienie ikony aplikacji w pasku zadań
if name == "nt":
    myappid = "maciejgarncarski.projektFTP.WdP.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(app_title)
        pixmap = QPixmap()

        if getattr(sys, "frozen", False):
            # If it's an executable set the base directory to sys._MEIPASS
            base_directory = sys._MEIPASS
        else:
            # Otherwise set it as the folder containing the main script
            base_directory = path.dirname(path.realpath("__file__"))

        assets_folder = path.join(base_directory, "assets")
        logo_path = path.join(assets_folder, "logo.png")
        pixmap.loadFromData(Path(logo_path).read_bytes())
        app_icon = QIcon(pixmap)
        self.setWindowIcon(app_icon)
        self.setFixedSize(400, 400)
        self.login_ui = None
        self.server_ui = None
        self.central_widget = QStackedWidget()

        self.setCentralWidget(self.central_widget)
        self.start_login_ui()

    def closeEvent(self, event):
        if ftp_client.ftp is not None:
            confirm_logout = ConfirmationBox(
                button_no_text="Anuluj",
                text="Czy na pewno chcesz się rozłączyć?",
                button_yes_text="Rozłącz",
                on_confirm=event.accept,
                on_reject=event.ignore,
            )
            confirm_logout.show()

    def start_login_ui(self):
        self.setFixedSize(400, 350)
        self.login_ui = LoginFTPWidget(
            self, start_server_ui=self.start_server_ui, main_window=self
        )
        self.central_widget.addWidget(self.login_ui)
        self.central_widget.setCurrentWidget(self.login_ui)

    def start_server_ui(self):
        self.setMinimumSize(650, 500)
        self.setMaximumSize(1300, 1000)
        self.server_ui = ServerWidget(self, start_login_ui=self.start_login_ui)
        self.central_widget.addWidget(self.server_ui)
        self.central_widget.setCurrentWidget(self.server_ui)


# Niestandardowa obsługa wyjątków, która pozwala na ponowne połączenie z serwerem FTP
def excepthook(exc_type, exc_value, exc_tb):
    ftp_client.reconnect()
    QtWidgets.QApplication.quit()


sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
