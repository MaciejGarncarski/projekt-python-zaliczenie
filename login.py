import sqlite3
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QDialog,
    QScrollArea,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from ftplib import FTP, all_errors
from constants import (
    default_ftp_settings,
    ftp_connection_errors,
    default_ftp_settings_description,
)
from ftp import ftp_client

from labeled_input import LabeledInput
from utils import delete_items_of_layout


class LoginFTPWidget(QWidget):
    def __init__(self, parent=None):
        super(LoginFTPWidget, self).__init__(parent)
        self.main_layout = QVBoxLayout()
        self.bottom_box = QVBoxLayout()
        self.button_box = QHBoxLayout()
        self.save_login_data_checkbox = None
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.error_message = None

        self.prepare_database()
        self.setLayout(self.main_layout)

        self.setWindowTitle("Połącz się z serwerem FTP")

        form_box = QFormLayout()

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

        form_box.setContentsMargins(0, 0, 0, 10)
        self.main_layout.addLayout(form_box)
        self.init_bottom_ui()
        self.setLayout(self.main_layout)

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

    def init_bottom_ui(self):
        self.save_login_data_checkbox = QCheckBox()
        self.save_login_data_checkbox.setText("Zapisz dane połączenia do bazy danych")

        default_settings_text = QLabel(default_ftp_settings_description)
        default_settings_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

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
        if self.error_message is not None:
            self.error_message.setParent(None)

        try:
            ftp_client.disconnect()
            ftp_client.connect(
                host=self.host.get_text(),
                port=int(self.port.get_text()),
                user=self.user.get_text(),
                password=self.password.get_text(),
            )

            if self.save_login_data_checkbox.isChecked():
                self.save_login_data()

            self.parent().parent().start_server_ui()

        except all_errors as error:
            error_message = str(error)
            try:
                error_code = error_message[:3]
                self.error_message = QLabel("Nie udało się połączyć z serwerem.")
                self.error_message.setStyleSheet("color: red; font-weight: semi-bold;")
                self.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)

                if ftp_connection_errors.get(error_code):
                    self.error_message.setText(
                        f"Błąd.\n{ftp_connection_errors.get(error_code)}"
                    )
                else:
                    self.error_message.setText(
                        f"Nie udało się połączyć z serwerem.\nBłąd: {error_message}"
                    )

                self.bottom_box.insertWidget(2, self.error_message)

            except TypeError:
                self.error_message.setText(
                    f"Nie udało się połączyć z serwerem.\nBłąd: {error_message}"
                )
                self.bottom_box.insertWidget(2, self.error_message)

    def init_login_data_dialog(self):
        dialog = SelectLoginInformation(self)
        dialog.exec()

    def set_form_values(self, host, port, user, password):
        self.host.set_text(host)
        self.port.set_text(port)
        self.user.set_text(user)
        self.password.set_text(password)

    def save_login_data(self):
        conn = sqlite3.connect("database.sqlite")
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


class SelectLoginInformation(QDialog):
    def __init__(self, ftp_widget):
        super().__init__()
        self.setWindowTitle("Wybierz dane połączenia")
        self.setFixedSize(500, 300)
        self.setObjectName("SelectLoginInformationDialog")
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.ftp_widget = ftp_widget

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.conn = sqlite3.connect("database.sqlite")
        self.cursor = self.conn.cursor()
        self.fetched_items = None

        self.create_items()

        scroll_area.setWidget(self.content_widget)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(scroll_area)

    def create_items(self):
        delete_items_of_layout(self.content_layout)
        conn = sqlite3.connect("database.sqlite")
        cursor = conn.cursor()
        cursor.execute(
            """
          SELECT itemId, host, user, port, password FROM login_data
           """
        )

        self.fetched_items = cursor.fetchall()
        for itemId, host, user, port, password in self.fetched_items:
            login_data = (itemId, host, port, user, password)

            login_data = LoginInformationItem(
                login_data,
                set_form_values=self.ftp_widget.set_form_values,
                parent=self.content_widget,
            )
            self.content_layout.addWidget(login_data)
        self.content_layout.addStretch()


class LoginInformationItem(QWidget):
    def __init__(
        self,
        login_data=None,
        set_form_values=None,
        parent=None,
    ):
        super().__init__(parent)
        itemId, host, port, user, password = login_data
        self.set_form_values = set_form_values
        self.setObjectName(f"item-{itemId}")

        item_layout = QHBoxLayout()
        login_label = QLabel(f"{user}@{host}:{port}")
        delete_button = QPushButton("Usuń")
        select_button = QPushButton("Wybierz")

        item_layout.addWidget(login_label)
        item_layout.addWidget(delete_button)
        item_layout.addWidget(select_button)

        delete_button.setFixedWidth(50)
        select_button.setFixedWidth(100)

        delete_button.clicked.connect(
            lambda: self.delete_item(itemId, host, port, user)
        )
        select_button.clicked.connect(
            lambda: self.select_item(host, port, user, password)
        )

        self.setLayout(item_layout)

    def delete_item(self, itemId, host, port, user):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Warning)
        message_box.setWindowTitle("Usuwanie danych połączenia")
        message_box.setText(
            f"Czy na pewno chcesz usunąć dane połączenia?\n{user}@{host}:{port}"
        )
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button_yes = message_box.button(QMessageBox.Yes)
        button_yes.setText("Usuń")
        button_no = message_box.button(QMessageBox.No)
        button_no.setText("Anuluj")

        message_box.setDefaultButton(QMessageBox.No)

        if message_box.clickedButton() == QMessageBox.No:
            message_box.close()

        if message_box.clickedButton() == QMessageBox.Yes:
            conn = sqlite3.connect("database.sqlite")
            cursor = conn.cursor()
            cursor.execute(
                """
            DELETE FROM login_data WHERE itemId = ?
            """,
                (itemId,),
            )
            conn.commit()
            self.parent().parent().findChild(QWidget, f"item-{itemId}").setParent(None)

        message_box.exec_()

    def select_item(self, host=None, port=None, user=None, password=None):
        self.set_form_values(host, str(port), user, password)
        self.parent().parent().parent().parent().close()
