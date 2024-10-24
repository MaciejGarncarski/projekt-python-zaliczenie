from pathlib import Path
from os import path

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QTreeWidget, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QProgressDialog, QLabel, \
    QFileDialog, QStyledItemDelegate, QInputDialog
from ftp import ftp_client
from utils import is_directory, clear_tree_widget, defer_ui_change

class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.setWindowTitle("Połączono z serwerem")
        self.current_path = CurrentPath()
        self.upload_widget = FileUploadWidget(self)
        self.file_tree_box = QTreeWidget()
        self.server_layout = QVBoxLayout()

        self.file_tree_box.setHeaderLabels(["Nazwa", "Rozmiar", "Data modyfikacji", "Akcje"])
        self.file_tree_box.setColumnWidth(0, 200)
        self.file_tree_box.setColumnWidth(1, 90)
        self.file_tree_box.setColumnWidth(2, 130)

        self.file_tree_box.setIconSize(QSize(24, 24))
        self.file_tree_box.itemDoubleClicked.connect(self.on_item_clicked)

        # górne przyciski
        toolbar_box = QHBoxLayout()
        go_back_button = QPushButton("Wstecz")
        go_back_button.clicked.connect(self.navigate_back)
        toolbar_box.addWidget(go_back_button)

        refresh_button = QPushButton("Odśwież")
        refresh_button.clicked.connect(lambda: self.show_file_tree('.'))
        toolbar_box.addWidget(refresh_button)

        home_button = QPushButton("Początkowa ścieżka")
        home_button.clicked.connect(lambda: self.navigate('/'))
        toolbar_box.addWidget(home_button)

        create_dir_button = QPushButton("Utwórz katalog")
        create_dir_button.clicked.connect(self.create_dir)
        toolbar_box.addWidget(create_dir_button)

        # dolne przyciski
        button_box = QHBoxLayout()
        self.logout_button = QPushButton("Rozłącz")
        self.logout_button.clicked.connect(self.log_out)
        button_box.addWidget(self.logout_button)
        button_box.addWidget(self.upload_widget.upload_button)

        self.server_layout.addWidget(self.current_path.current_path_label)
        self.server_layout.addLayout(toolbar_box)
        self.server_layout.addWidget(self.file_tree_box)
        self.server_layout.addLayout(button_box)
        self.setLayout(self.server_layout)

        self.show_file_tree(".")

    def show_file_tree(self, directory="."):
        clear_tree_widget(self.file_tree_box)
        file_list = ftp_client.list_files(directory, self.file_tree_box)
        self.file_tree_box.addTopLevelItems(file_list)

    def navigate_back(self):
        if self.current_path.directory_path != "/":
            ftp_client.cwd("../")
            self.current_path.update_path()
            self.show_file_tree()

    def navigate(self, navigation_path):
        ftp_client.cwd(navigation_path)

        if navigation_path == '/':
            self.show_file_tree('.')
        else:
            self.show_file_tree(ftp_client.get_path())

        self.current_path.update_path()

    def log_out(self):
        ftp_client.log_out()
        self.parent().parent().start_login_ui()

    def on_item_clicked(self, clicked_item, col):
        if clicked_item.is_directory:
            directory_path = clicked_item.text(0)
            self.navigate(self.current_path.directory_path + "/" + directory_path)

    def create_dir(self):
        directory_path = self.current_path.directory_path
        new_directory_name = QInputDialog.getText(self, "Utwórz katalog", "Nazwa katalogu:")[0]
        if new_directory_name:
            formatted_path = "/" if directory_path == "/" else directory_path + "/"
            ftp_client.create_dir(formatted_path + new_directory_name)
            self.show_file_tree()


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
        current_path = self.parent().current_path.directory_path
        remote_path = current_path if current_path == '/' else current_path + '/'

        if self.select_file_dialog.exec_():
            file_names = self.select_file_dialog.selectedFiles()
            if file_names:
                self.file = str(Path(file_names[0]))
                self.upload_file(remote_path)
                self.parent().show_file_tree()

    def upload_file(self, remote_path):
        file_size = path.getsize(self.file)
        file_name = path.basename(self.file)

        progress_dialog = ProgressBar(file_size)
        ftp_client.upload_file(self.file, remote_path + file_name, progress_dialog.handle)
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
        self.setFixedSize(300, 150)

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