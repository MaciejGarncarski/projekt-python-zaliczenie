from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
import sys

import os
import ctypes

from constants import app_title
from login import LoginFTPWidget

app = QApplication(sys.argv)

## ustawia ikonkę aplikacji na windowsie
if os.name == 'nt':
    myappid = 'maciejgarncarski.projektFTP.WdP.1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(app_title)
        pixmap = QPixmap()
        pixmap.loadFromData(Path("ftp.jpeg").read_bytes() )
        app_icon = QIcon(pixmap)
        self.setWindowIcon(app_icon)
        self.setFixedSize(400, 400)
        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setCentralWidget(LoginFTPWidget())

        login_widget = LoginFTPWidget(self)
        self.central_widget.addWidget(login_widget)

window = MainWindow()
window.show()

if __name__ == '__main__':
    sys.exit(app.exec())