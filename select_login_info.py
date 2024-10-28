from PyQt5.QtWidgets import (
    QDialog,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
import sqlite3

from dialog import ConfirmationBox
from utils import delete_items_of_layout


class SelectLoginInformation(QDialog):
    def __init__(self, parent=None, set_form_values=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz dane połączenia")
        self.setFixedSize(500, 300)
        self.setObjectName("SelectLoginInformationDialog")
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.set_form_values = set_form_values

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
        for item_id, host, user, port, password in self.fetched_items:
            login_data = (item_id, host, port, user, password)

            login_data = LoginInformationItem(
                login_data,
                set_form_values=self.set_form_values,
                parent=self.content_widget,
                close_dialog=self.close,
                remove_widget=self.content_layout.removeWidget,
            )
            self.content_layout.addWidget(login_data)
        self.content_layout.addStretch()


class LoginInformationItem(QWidget):
    def __init__(
        self,
        login_data=None,
        set_form_values=None,
        parent=None,
        close_dialog=None,
        remove_widget=None,
    ):
        super().__init__(parent)
        item_id, host, port, user, password = login_data
        self.set_form_values = set_form_values
        self.close_dialog = close_dialog
        self.remove_widget = remove_widget

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
            lambda: self.delete_item(item_id, host, port, user)
        )
        select_button.clicked.connect(
            lambda: self.select_item(host, port, user, password)
        )

        self.setLayout(item_layout)

    def delete_item(self, item_id, host, port, user):
        def on_confirm():
            conn = sqlite3.connect("database.sqlite")
            cursor = conn.cursor()
            cursor.execute(
                """
            DELETE FROM login_data WHERE itemId = ?
            """,
                (item_id,),
            )
            conn.commit()
            self.remove_widget(self)
            self.setParent(None)

        message_box = ConfirmationBox(
            title="Usuwanie danych połączenia",
            text=f"Czy na pewno chcesz usunąć dane połączenia?\n{user}@{host}:{port}",
            on_confirm=on_confirm,
        )
        message_box.show()

    def select_item(self, host=None, port=None, user=None, password=None):
        self.set_form_values(host, str(port), user, password)
        self.close_dialog()
