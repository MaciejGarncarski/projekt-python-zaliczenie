import sqlite3
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from ftplib import all_errors
from constants import (
    default_ftp_settings,
    ftp_connection_errors,
    default_ftp_settings_description,
)
from dialog import NotificationBox
from ftp import ftp_client

from labeled_input import LabeledInput
from select_login_info import SelectLoginInformation


class LoginFTPWidget(QWidget):
    def __init__(self, parent=None, start_server_ui=None, main_window=None):
        super(LoginFTPWidget, self).__init__(parent)
        self.save_login_data_checkbox = None
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.error_message = None
        self.start_server_ui = start_server_ui
        self.main_window = main_window

        self.prepare_database()
        self.main_layout = QVBoxLayout()
        self.bottom_box = QVBoxLayout()
        self.button_box = QHBoxLayout()
        self.setWindowTitle("Połącz się z serwerem FTP")
        form_box = QFormLayout()
        form_box.setContentsMargins(0, 0, 0, 10)

        self.host = LabeledInput(
            placeholder="Host",
            form_box=form_box,
            default_text=default_ftp_settings["host"],
        )

        self.port = LabeledInput(
            placeholder="Port", form_box=form_box, default_text="21"
        )

        self.user = LabeledInput(
            placeholder="Użytkownik",
            form_box=form_box,
            default_text=default_ftp_settings["user"],
        )

        self.password = LabeledInput(
            placeholder="Hasło",
            form_box=form_box,
            is_password=True,
            default_text=default_ftp_settings["password"],
        )

        self.main_layout.addLayout(form_box)
        self.setLayout(self.main_layout)
        self.init_bottom_ui()

    @staticmethod
    def prepare_database():
        conn = sqlite3.connect("database.sqlite")
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS login_data (
            itemId INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            user TEXT NOT NULL,
            port INTEGER NOT NULL,
            password TEXT NOT NULL
        )
        """
        )
        conn.close()

    def init_bottom_ui(self):
        self.save_login_data_checkbox = QCheckBox()
        self.save_login_data_checkbox.setText("Zapisz dane połączenia do bazy danych")

        default_settings_text = QLabel(default_ftp_settings_description)
        default_settings_text.setTextInteractionFlags(Qt.TextSelectableByMouse)

        login_button = QPushButton("Połącz z serwerem")
        login_button.clicked.connect(self.login_ftp)

        select_login_data = QPushButton("Wybierz dane połączenia")
        select_login_data.clicked.connect(self.init_login_data_dialog)

        self.bottom_box = QVBoxLayout()
        self.bottom_box.setSpacing(20)

        self.button_box.addWidget(select_login_data)
        self.button_box.addWidget(login_button)

        self.bottom_box.addWidget(self.save_login_data_checkbox)
        self.bottom_box.addLayout(self.button_box)
        self.bottom_box.addStretch()
        self.bottom_box.addWidget(default_settings_text)
        self.main_layout.addLayout(self.bottom_box)

    def login_ftp(self):
        try:
            ftp_client.log_out()
            ftp_client.connect(
                host=self.host.get_text(),
                port=int(self.port.get_text()),
                user=self.user.get_text(),
                password=self.password.get_text(),
            )

            self.start_server_ui()

            if self.save_login_data_checkbox.isChecked():
                self.save_login_data()
                notification_dialog = NotificationBox(
                    "Połączono z serwerem i zapisano dane połączenia."
                )
                notification_dialog.show()
            else:
                notification_dialog = NotificationBox("Połączono z serwerem.")
                notification_dialog.show()

        except all_errors as error:
            self.main_window.setFixedSize(400, 400)
            error_message = str(error)
            try:
                error_code = int(error_message[:3])

                if ftp_connection_errors.get(error_code):
                    notification_dialog = NotificationBox(
                        text=f"Błąd.\n{ftp_connection_errors.get(error_code)}",
                        icon="error",
                    )
                    notification_dialog.show()
                else:
                    notification_dialog = NotificationBox(
                        text=f"Nie udało się połączyć z serwerem.\nBłąd: {error_message}",
                        icon="error",
                    )
                    notification_dialog.show()

            except TypeError:
                notification_dialog = NotificationBox(
                    text=f"Nie udało się połączyć z serwerem.\nBłąd: {error_message}",
                    icon="error",
                )
                notification_dialog.show()

    def init_login_data_dialog(self):
        dialog = SelectLoginInformation(self, set_form_values=self.set_form_values)
        dialog.exec()

    def set_form_values(self, host, port, user, password):
        self.host.set_text(host)
        self.port.set_text(port)
        self.user.set_text(user)
        self.password.set_text(password)

    def save_login_data(self):
        conn = sqlite3.connect("database.sqlite")
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO login_data (host, user, port, password) VALUES (?, ?, ?, ?)
            """,
                (
                    self.host.get_text(),
                    self.user.get_text(),
                    int(self.port.get_text()),
                    self.password.get_text(),
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Błąd bazy danych: {e}")
        finally:
            conn.close()
