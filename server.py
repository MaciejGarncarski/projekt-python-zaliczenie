from time import sleep

from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressDialog,
    QHBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView,
)
from pathlib import Path
from os import path
from ftp import ftp_client
from utils import is_directory, clear_tree_widget, defer_ui_change


class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.setWindowTitle("Połączono z serwerem")
        self.start_login_ui = None
        self.current_path = CurrentPath()

        self.upload_widget = FileUploadWidget(self)
        self.server_layout = QVBoxLayout()
        self.logout_button = QPushButton("Wyloguj")
        self.file_tree_box = QTreeWidget()
        self.file_tree_header = self.file_tree_box.header()
        self.file_tree_box.setColumnWidth(0, 200)
        self.file_tree_box.setColumnWidth(1, 130)
        self.file_tree_box.setIconSize(QSize(24, 24))
        self.file_tree_box.itemDoubleClicked.connect(self.on_item_clicked)
        self.server_layout.addWidget(self.current_path.current_path_label)
        button_box = QHBoxLayout()

        self.logout_button.clicked.connect(self.log_out)
        button_box.addWidget(self.logout_button)
        button_box.addWidget(self.upload_widget.upload_button)

        self.setLayout(self.server_layout)
        self.show_file_tree(".")
        self.server_layout.addWidget(self.file_tree_box)
        self.server_layout.addLayout(button_box)


    def show_file_tree(self, directory):
        file_list = ftp_client.list_files(directory)
        self.file_tree_box.addTopLevelItem(QTreeWidgetItem(["..", "  ", "  "]))
        self.file_tree_box.setHeaderLabels(["Nazwa", "Rozmiar", "Data modyfikacji"])


        for file_name, file_size, file_date in file_list:
            file_item = FileItemWidget(self.file_tree_box, file_name, file_size, file_date)
            self.file_tree_box.addTopLevelItem(file_item)


    def on_item_clicked(self, clicked_item, col):
        if clicked_item.text(0) == "..":
            self.navigate_back()
            return

        if clicked_item.is_directory:
            directory_path = clicked_item.text(0)
            self.navigate(self.current_path.directory_path + "/" + directory_path)


    def navigate_back(self):
        if self.current_path.directory_path != "/":
            ftp_client.cwd("../")
            self.current_path.update_path()
            self.clear_tree()

    def clear_tree(self):
        def clear():
            clear_tree_widget(self.file_tree_box)
            self.show_file_tree(".")

        defer_ui_change(clear)

    def navigate(self, navigation_path):
        ftp_client.cwd(navigation_path)
        self.current_path.update_path()
        clear_tree_widget(self.file_tree_box)
        defer_ui_change(lambda: self.show_file_tree(navigation_path))

    def log_out(self):
        ftp_client.disconnect()
        self.parent().parent().start_login_ui()


class FileItemWidget(QTreeWidgetItem):
    def __init__(self, parent=None, file_name=None, file_size=None, file_date=None):
        super(QTreeWidgetItem, self).__init__(parent)
        file_icon = QIcon('file.png')
        folder_icon = QIcon('folder.png')
        self.is_directory = False
        self.setText(0, file_name)

        # Jeżeli file_size == '-', jest to folder
        if file_size is '-':
            self.setIcon(0, folder_icon)
            self.setText(1, '-')
            self.is_directory = True
        else:
            self.is_directory = False
            self.setIcon(0, file_icon)
            self.setText(1, file_size)

        if file_date is '-':
            self.setText(2, '-')
        else:
            self.setText(2, file_date)

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

        progress_dialog = ProgressBar(file_size)
        ftp_client.upload_file(self.file, file_name, progress_dialog.handle)
        progress_dialog.close()


class CurrentPath(QWidget):
    def __init__(self):
        super().__init__()
        self.directory_path = ftp_client.get_path()
        self.current_path_label = QLabel(f"Aktualna ścieżka: {self.directory_path}")

    def update_path(self):
        self.directory_path = ftp_client.get_path()
        self.current_path_label.setText(f"Aktualna ścieżka: {self.directory_path}")


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