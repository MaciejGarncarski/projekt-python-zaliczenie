from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton
from ftplib import FTP
from constants import default_ftp_settings
from PyQt6.QtCore import Qt
from labeled_input import LabeledInput

class LoginFTPWidget(QWidget):
    def init_ui(self, MainWindow):
        self.setWindowTitle("Połącz się z serwerem FTP")
        self.setWindowTitle("Połącz się z serwerem FTP")

        main_layout = QVBoxLayout()
        form_box = QFormLayout()
        host = LabeledInput(placeholder="Host", form_box=form_box)
        port = LabeledInput(placeholder="Port", form_box=form_box, default_text='21')
        user = LabeledInput(placeholder="Użytkownik", form_box=form_box)
        password = LabeledInput(placeholder="Hasło", form_box=form_box, is_password=True)

        default_settings_layout = QVBoxLayout()

        default_settings = QLabel(f"""
        Testowy serwer FTP:
          - host: {default_ftp_settings["host"]}
          - port: {default_ftp_settings["port"]}
          - użytkownik: {default_ftp_settings["user"]}
          - hasło: {default_ftp_settings["password"]}
        """)

        default_settings.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        default_settings_layout.addWidget(default_settings)

        def login():
            host_text = host.get_text()
            port_text = port.get_text()
            user_text = user.get_text()
            password_text = password.get_text()

            self.login_ftp(self, host=host_text, port=port_text, user=user_text, password=password_text)

        login_button = QPushButton("Połącz z serwerem")
        login_button.clicked.connect(login)

        main_layout.addLayout(form_box)
        main_layout.addLayout(default_settings_layout)
        main_layout.addWidget(login_button)

        self.setLayout(main_layout)
        MainWindow.setCentralWidget(self)

    @staticmethod
    def login_ftp(self, host=None, port=22, user=None, password=None):
        print(self.is_loading)
        self.is_loading = True
        print(self.is_loading)

        ftp = FTP(timeout=20)

        print(host, int(port), user, password)

        ftp.connect(host=host, port=int(port))
        ftp.login(user=user, passwd=password)
        print(ftp.pwd())