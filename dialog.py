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
    QFileDialog,
    QHBoxLayout,
)
from os import path
import time
from constants import icons, dialog_width, dialog_height
from labeled_input import LabeledInput
from utils import convert_size, convert_time


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
        self, title="Wprowadź dane", input_title="Wprowadź dane", on_confirm=None, default_value=""
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
        self.input = LabeledInput(input_title, form_box=form_box, default_text=default_value)
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
    remaining_size = pyqtSignal(int)
    speed_changed = pyqtSignal(float)
    time_remaining = pyqtSignal(int)

    def __init__(self, file_path, remote_path, ftp_client):
        super().__init__()
        self.file_path = file_path
        self.remote_path = remote_path
        self.ftp_client = ftp_client

    def run(self):
        self.ftp_client.reconnect()
        file_size = path.getsize(self.file_path)
        uploaded_size = 0
        start_time = time.time()

        def handle_block(block):
            nonlocal uploaded_size
            uploaded_size += len(block)
            progress = int((uploaded_size / file_size) * 100)
            self.progress.emit(progress)
            elapsed_time = time.time() - start_time
            speed = uploaded_size / elapsed_time if elapsed_time > 0 else 0
            remaining_bytes = path.getsize(self.file_path) - uploaded_size
            time_left = remaining_bytes / speed if speed > 0 else 0
            self.speed_changed.emit(speed)
            self.time_remaining.emit(int(time_left))
            self.remaining_size.emit(remaining_bytes)

        self.ftp_client.upload_file(self.file_path, self.remote_path, handle_block)


class UploadProgressDialog(QDialog):
    def __init__(
        self,
        file_path,
        remote_path,
        ftp_client=None,
        redraw_file_tree=None,
        parent=None,
    ):
        super(UploadProgressDialog, self).__init__(parent)
        self.setWindowTitle("Przesyłanie pliku...")
        self.setFixedSize(dialog_width, 150)
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.ftp_client = ftp_client
        self.remote_path = remote_path
        self.redraw_file_tree = redraw_file_tree
        self.is_uploading = True

        layout = QVBoxLayout(self)
        self.label = QLabel("Przesyłanie pliku...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.cancel_button = QPushButton("Anuluj")
        self.cancel_button.clicked.connect(self.cancel_upload)
        self.remaining_size_label = QLabel("Pozostało: 0")
        self.speed_label = QLabel("Prędkość wysyłania: 0")
        self.time_remained_label = QLabel("Pozostały czas: 0")

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.remaining_size_label)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.time_remained_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.upload_thread = UploadThread(file_path, self.remote_path, self.ftp_client)
        self.upload_thread.progress.connect(self.update_progress)
        self.upload_thread.remaining_size.connect(self.update_size)
        self.upload_thread.speed_changed.connect(self.update_speed)
        self.upload_thread.time_remaining.connect(self.update_time)
        self.upload_thread.start()

    def show(self):
        self.exec_()
        self.is_uploading = True

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.is_uploading = True

        if value == 100:
            self.is_uploading = False
            self.close()
            upload_notification = NotificationBox(
                text=f"Przesłano plik {self.remote_path}", icon="info"
            )
            upload_notification.show()
            self.redraw_file_tree()

    def update_size(self, size):
        self.remaining_size_label.setText(f"Pozostało: {convert_size(size)}")

    def update_speed(self, speed):
        self.speed_label.setText(f"Prędkość pobierania: {convert_size(speed)}/s")

    def update_time(self, time):
        self.time_remained_label.setText(f"Pozostały czas: {convert_time(time)}")

    def cancel_upload(self):
        self.close()

    def closeEvent(self, event):
        if not self.is_uploading:
            event.accept()
            return

        def on_confirm():
            self.upload_thread.terminate()
            confirmation_dialog.close()
            self.close()
            self.redraw_file_tree()
            cancel_notification = NotificationBox(
                text=f"Anulowano przesyłanie pliku", icon="warning"
            )
            cancel_notification.show()

        confirmation_dialog = ConfirmationBox(
            text="Czy na pewno chcesz przerwać przesyłanie pliku?",
            on_confirm=on_confirm,
            on_reject=event.ignore,
        )
        confirmation_dialog.show()


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    remaining_size = pyqtSignal(int)
    speed_changed = pyqtSignal(float)
    time_remaining = pyqtSignal(int)

    def __init__(self, save_path, remote_path, ftp_client):
        super().__init__()
        self.remote_path = remote_path
        self.ftp_client = ftp_client
        self.save_path = save_path

    def run(self):
        self.ftp_client.reconnect()
        file_size = self.ftp_client.ftp.size(self.remote_path)
        download_size = 0
        start_time = time.time()

        def handle_block(block):
            nonlocal download_size
            download_size += len(block)
            progress = int((download_size / file_size) * 100)
            elapsed_time = time.time() - start_time
            speed = download_size / elapsed_time if elapsed_time > 0 else 0
            remaining_bytes = file_size - download_size
            time_left = remaining_bytes / speed if speed > 0 else 0
            self.progress.emit(progress)
            self.remaining_size.emit(remaining_bytes)
            self.speed_changed.emit(speed)
            self.time_remaining.emit(int(time_left))

        self.ftp_client.download_file(self.save_path, self.remote_path, handle_block)


class DownloadProgressDialog(QDialog):
    def __init__(
        self,
        remote_path,
        ftp_client=None,
        parent=None,
    ):
        super(DownloadProgressDialog, self).__init__(parent)
        self.setWindowTitle("Pobieranie pliku...")
        self.setFixedSize(dialog_width, 150)
        logo_path = path.join(path.dirname(__file__), r"assets\logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.ftp_client = ftp_client
        self.remote_path = remote_path
        self.save_path = None
        self.is_downloaded = False

        layout = QVBoxLayout(self)
        self.label = QLabel("Pobieranie pliku...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.cancel_button = QPushButton("Anuluj")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.speed_label = QLabel("Prędkość pobierania: 0")
        self.remaining_size_label = QLabel("Pozostało: 0")
        self.time_remaining_label = QLabel("Pozostały czas: 0")

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.remaining_size_label)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.time_remaining_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def show(self):
        self.is_downloaded = False
        save_path, _ = QFileDialog.getSaveFileName(
            None, "Zapisz plik", self.remote_path
        )
        if save_path:
            self.save_path = save_path
            self.download_thread = DownloadThread(
                self.save_path, self.remote_path, self.ftp_client
            )
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.remaining_size.connect(self.update_size)
            self.download_thread.speed_changed.connect(self.update_speed)
            self.download_thread.time_remaining.connect(self.update_time_remaining)
            self.download_thread.start()
            self.exec_()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.is_downloaded = True
            self.close()
            upload_notification = NotificationBox(
                text=f"Pobrano plik\n{self.remote_path}\ndo katalogu\n{self.save_path}",
            )
            upload_notification.show()

    def update_size(self, size):
        self.remaining_size_label.setText(f"Pozostało: {convert_size(size)}")

    def update_speed(self, speed):
        self.speed_label.setText(f"Prędkość pobierania: {convert_size(speed)}/s")

    def update_time_remaining(self, time_remaining):
        self.time_remaining_label.setText(
            f"Pozostały czas: {convert_time(time_remaining)}"
        )

    def cancel_download(self):
        self.close()

    def closeEvent(self, event):
        if self.is_downloaded:
            event.accept()
            return

        def on_confirm():
            self.download_thread.terminate()
            confirmation_dialog.close()
            self.close()
            cancel_notification = NotificationBox(
                text=f"Anulowano pobieranie pliku", icon="warning"
            )
            cancel_notification.show()

        confirmation_dialog = ConfirmationBox(
            text="Czy na pewno chcesz przerwać pobieranie pliku?",
            on_confirm=on_confirm,
            on_reject=event.ignore,
        )
        confirmation_dialog.show()
