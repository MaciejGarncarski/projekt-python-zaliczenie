from time import sleep

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressDialog,
    QHBoxLayout,
)
from pathlib import Path
from os import path
from ftp import ftp_client


class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.setWindowTitle("Połączono z serwerem")
        self.setFixedSize(400, 400)
        self.start_login_ui = None
        self.current_path = QLabel(ftp_client.get_path())
        self.upload_widget = FileUploadWidget(self)

        self.server_layout = QVBoxLayout()
        self.logout_button = QPushButton("Wyloguj")
        self.server_layout.addWidget(self.current_path)
        self.server_layout.addStretch()
        button_box = QHBoxLayout()
        button_box.addWidget(self.logout_button)
        button_box.addWidget(self.upload_widget.upload_button)
        self.server_layout.addLayout(button_box)
        self.logout_button.clicked.connect(self.log_out)
        self.setLayout(self.server_layout)
        self.show_file_tree()

    def show_file_tree(self):
        file_tree_box = QVBoxLayout()
        file_list = ftp_client.list_files()
        for file in file_list:
            file_name_label = QLabel(file)
            file_tree_box.addWidget(file_name_label)

        self.server_layout.addLayout(file_tree_box)

    def log_out(self):
        ftp_client.disconnect()
        self.parent().parent().start_login_ui()


class FileUploadWidget(QWidget):
    def __init__(self, parent=None):
        super(FileUploadWidget, self).__init__(parent)
        self.upload_button = QPushButton("Prześlij plik")
        self.upload_button.clicked.connect(self.get_file)
        self.select_file_dialog = None
        self.file = None

    def get_file(self):
        self.select_file_dialog = QFileDialog()
        self.select_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.select_file_dialog.setViewMode(QFileDialog.Detail)

        if self.select_file_dialog.exec_():
            file_names = self.select_file_dialog.selectedFiles()
            if file_names:
                self.file = str(Path(file_names[0]))
                self.upload_file()

    def upload_file(self):
        file_size = path.getsize(self.file)
        file_name = path.basename(self.file)
        ftp_client.reconnect()

        progress_dialog = ProgressBar(file_size)
        ftp_client.upload_file(self.file, file_name, progress_dialog.handle)

        progress_dialog.close()


class ProgressBar(QProgressDialog):
    def __init__(self, file_size):
        super().__init__()
        self.last_shown_percent = 0
        self.size_written = 0
        self.file_size = file_size
        self.setMinimumDuration(0)
        self.setWindowTitle("Przesyłanie...")
        self.setModal(True)
        self.setCancelButton(None)

        self.setValue(0)
        self.setMinimum(0)
        self.setMaximum(100)

        self.show()

    def handle(self, block):
        self.size_written += 8192
        percent_complete = round((self.size_written / self.file_size) * 100)
        self.setValue(self.last_shown_percent)

        if self.last_shown_percent != percent_complete:
            self.last_shown_percent = percent_complete
