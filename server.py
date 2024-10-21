from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from ftp import ftp_client


class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.setWindowTitle("Połączono z serwerem")
        self.setFixedSize(400, 400)
        self.start_login_ui = None
        self.current_path = QLabel(ftp_client.pwd())

        server_layout = QVBoxLayout()
        self.logout_button = QPushButton("Wyloguj")
        server_layout.addWidget(self.current_path)
        server_layout.addStretch()
        server_layout.addWidget(self.logout_button)
        self.logout_button.clicked.connect(self.log_out)
        self.setLayout(server_layout)

        ftp_client.list_files()

    def log_out(self):
        ftp_client.disconnect()
        self.parent().parent().start_login_ui()
