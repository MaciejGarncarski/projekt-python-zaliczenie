from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout, QDialog
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

        save_login_information = QCheckBox()
        save_login_information.setText("Zapisz dane logowania")

        default_settings = QLabel(f"""
Testowy serwer FTP:
  - host: {default_ftp_settings["host"]}
  - port: {default_ftp_settings["port"]}
  - użytkownik: {default_ftp_settings["user"]}
  - hasło: {default_ftp_settings["password"]}
        """)

        default_settings.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        def login():
            host_text = host.get_text()
            port_text = port.get_text()
            user_text = user.get_text()
            password_text = password.get_text()

            self.login_ftp(self, host=host_text, port=port_text, user=user_text, password=password_text)

        login_button = QPushButton("Połącz z serwerem")
        login_button.clicked.connect(login)

        select_login_information = QPushButton("Załaduj dane logowania")
        select_login_information.clicked.connect(self.show_select_login_information)

        bottom_box = QVBoxLayout()
        bottom_box.setSpacing(20)
        bottom_box.setContentsMargins(0, 10, 0, 10)

        button_box = QHBoxLayout()
        button_box.addWidget(select_login_information)
        button_box.addWidget(login_button)

        main_layout.addLayout(form_box)
        bottom_box.addWidget(save_login_information)
        bottom_box.addLayout(button_box)
        bottom_box.addStretch()
        bottom_box.addWidget(default_settings)
        main_layout.addLayout(bottom_box)

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

    def show_select_login_information(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Załaduj dane logowania")
        dialog.exec()


