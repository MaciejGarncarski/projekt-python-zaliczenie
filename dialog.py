from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialogButtonBox,
    QMessageBox,
    QVBoxLayout,
    QFormLayout,
    QDialog,
    QLabel,
    QWidget,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
)
from os import path
from constants import icons, dialog_width, dialog_height
from labeled_input import LabeledInput


class ConfirmationBox(QMessageBox):
    def __init__(
        self,
        title="Potwierdź",
        text=None,
        button_yes_text="Potwierdź",
        button_no_text="Anuluj",
        on_confirm=None,
        on_reject=None,
    ):
        super().__init__()
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button_yes = self.button(QMessageBox.Yes)
        button_yes.setText(button_yes_text)
        button_no = self.button(QMessageBox.No)
        button_no.setText(button_no_text)
        self.setDefaultButton(QMessageBox.No)
        self.on_confirm = on_confirm
        self.on_reject = on_reject

    def show(self):
        result = self.exec_()

        if result == QMessageBox.No:
            if self.on_reject is not None:
                self.on_reject()
            self.close()

        if result == QMessageBox.Yes:
            self.on_confirm()


class NotificationBox(QMessageBox):
    def __init__(self, text=None, icon="info"):
        super().__init__()
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.icon = icon
        self.text = text
        self.setFixedSize(dialog_width, dialog_height)

    def show(self):
        self.setWindowTitle("Powiadomienie")
        self.setText(self.text or "Powiadomienie")
        self.setIcon(icons.get(self.icon) or icons.get("info"))
        self.setModal(True)
        self.setStandardButtons(QMessageBox.Yes)
        button_yes = self.button(QMessageBox.Yes)
        button_yes.setText("Ok")

        result = self.exec_()

        if result == QMessageBox.Yes:
            self.close()


class InputDialog(QDialog):
    def __init__(
        self, title="Wprowadź dane", input_title="Wprowadź dane", on_confirm=None
    ):
        super().__init__()
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.setWindowTitle(title)
        self.setFixedSize(dialog_width, dialog_height)
        self.on_confirm = on_confirm

        form_widget = QWidget()
        form_box = QFormLayout()
        self.setLayout(form_box)
        self.input = LabeledInput(input_title, form_box=form_box)
        form_box.addWidget(self.input)
        form_widget.setLayout(form_box)
        main_layout = QVBoxLayout()
        main_layout.addWidget(form_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        button_box.button(QDialogButtonBox.Ok).setText("Potwierdź")
        button_box.button(QDialogButtonBox.Cancel).setText("Anuluj")

        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def show(self):
        result = self.exec_()

        if result == QMessageBox.Rejected:
            self.close()

        if result == QMessageBox.Accepted:
            self.on_confirm()
            self.close()

    def get_input(self):
        return self.input.get_text()


class UploadThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, file_path, remote_path, ftp_client):
        super().__init__()
        self.file_path = file_path
        self.remote_path = remote_path
        self.ftp_client = ftp_client

    def run(self):
        self.ftp_client.reconnect()
        file_size = path.getsize(self.file_path)
        uploaded_size = 0

        def handle_block(block):
            nonlocal uploaded_size
            uploaded_size += len(block)
            progress = int((uploaded_size / file_size) * 100)
            self.progress.emit(progress)

        self.ftp_client.upload_file(self.file_path, self.remote_path, handle_block)


class ProgressDialog(QDialog):
    def __init__(
        self,
        file_path,
        remote_path,
        ftp_client=None,
        redraw_file_tree=None,
        parent=None,
    ):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle("Przesyłanie pliku...")
        self.setFixedSize(dialog_width, dialog_height)
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.ftp_client = ftp_client
        self.remote_path = remote_path
        self.redraw_file_tree = redraw_file_tree

        layout = QVBoxLayout(self)
        self.label = QLabel("Przesyłanie pliku...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.cancel_button = QPushButton("Anuluj")
        self.cancel_button.clicked.connect(self.cancel_upload)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.upload_thread = UploadThread(file_path, self.remote_path, self.ftp_client)
        self.upload_thread.progress.connect(self.update_progress)
        self.upload_thread.start()

    def show(self):
        self.exec_()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.close()
            upload_notification = NotificationBox(
                text=f"Przesłano plik {self.remote_path}", icon="info"
            )
            upload_notification.show()
            self.redraw_file_tree()

    def cancel_upload(self):
        self.upload_thread.terminate()
        self.close()
        cancel_notification = NotificationBox(
            text=f"Anulowano przesyłanie pliku", icon="warning"
        )
        cancel_notification.show()
        self.redraw_file_tree()
