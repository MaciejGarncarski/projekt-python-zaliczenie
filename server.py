from datetime import datetime
from pathlib import Path
from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QTreeWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QProgressDialog,
    QLabel,
    QFileDialog,
    QInputDialog,
    QTreeWidgetItem,
)

from constants import dialog_width, dialog_height
from dialog import NotificationBox, ConfirmationBox, InputDialog, ProgressDialog
from ftp import ftp_client
from utils import is_directory, clear_tree_widget, convert_size


class ServerWidget(QWidget):
    def __init__(self, parent=None, start_login_ui=None):
        super(ServerWidget, self).__init__(parent)
        self.setWindowTitle("Połączono z serwerem")
        self.current_path = CurrentPath()
        self.upload_widget = FileUploadWidget(
            self,
            redraw_file_tree=self.redraw_file_tree,
        )
        self.start_login_ui = start_login_ui

        # drzewo plików
        self.file_tree_box = QTreeWidget()
        self.file_tree_box.setHeaderLabels(
            ["Nazwa", "Rozmiar", "Data modyfikacji", "Akcje"]
        )
        self.file_tree_box.setIndentation(0)
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
        refresh_button.clicked.connect(lambda: self.redraw_file_tree())
        toolbar_box.addWidget(refresh_button)

        home_button = QPushButton("Początkowa ścieżka")
        home_button.clicked.connect(lambda: self.navigate("/"))
        toolbar_box.addWidget(home_button)

        create_dir_button = QPushButton("Utwórz katalog")
        create_dir_button.clicked.connect(self.create_dir)
        toolbar_box.addWidget(create_dir_button)

        # dolne przyciski
        button_box = QHBoxLayout()
        self.logout_button = QPushButton("Rozłącz")
        confirm_logout = ConfirmationBox(
            button_no_text="Anuluj",
            text="Czy na pewno chcesz się rozłączyć?",
            button_yes_text="Rozłącz",
            on_confirm=self.log_out,
        )
        self.logout_button.clicked.connect(lambda: confirm_logout.show())
        button_box.addWidget(self.logout_button)
        button_box.addWidget(self.upload_widget.upload_button)
        self.upload_widget.upload_button.clicked.connect(
            lambda: self.upload_widget.get_file(self.current_path.directory_path)
        )

        self.server_layout = QVBoxLayout()
        self.server_layout.addWidget(self.current_path.current_path_label)
        self.server_layout.addLayout(toolbar_box)
        self.server_layout.addWidget(self.file_tree_box)
        self.server_layout.addLayout(button_box)
        self.setLayout(self.server_layout)

        self.redraw_file_tree()

    def redraw_file_tree(self, directory="."):
        clear_tree_widget(self.file_tree_box)
        files = ftp_client.list_files(directory)
        file_list = []

        if len(files) == 0:
            no_files_widget = NoFilesWidget(parent=self.file_tree_box)
            file_list.append(no_files_widget)
            self.file_tree_box.setItemWidget(no_files_widget, 0, no_files_widget.label)
            self.file_tree_box.addTopLevelItems(file_list)
            self.file_tree_box.setFirstItemColumnSpanned(no_files_widget, True)
            return

        for file_name in files:
            formatted_file_name = (
                file_name
                if directory == "."
                else file_name.replace(directory + "/", "", 1)
            )

            if is_directory(ftp_client.ftp, file_name):
                file_data = (formatted_file_name, "-", "-")
                file_list.append(
                    FileItemWidget(
                        parent=self.file_tree_box,
                        redraw_file_tree=self.redraw_file_tree,
                        file_data=file_data,
                    )
                )
                continue

            file_size_bytes = ftp_client.ftp.size(file_name)
            modified_time = ftp_client.ftp.voidcmd(f"MDTM {file_name}")
            file_formatted_size = convert_size(file_size_bytes)
            modified_time = str(datetime.strptime(modified_time[4:], "%Y%m%d%H%M%S"))
            file_data = (formatted_file_name, file_formatted_size, modified_time)
            file_item = FileItemWidget(
                parent=self.file_tree_box,
                redraw_file_tree=self.redraw_file_tree,
                file_data=file_data,
            )
            file_list.append(file_item)

        self.file_tree_box.addTopLevelItems(file_list)

    def navigate_back(self):
        if self.current_path.directory_path != "/":
            ftp_client.cwd("../")
            self.current_path.update_path()
            self.redraw_file_tree()

    def navigate(self, navigation_path):
        ftp_client.cwd(navigation_path)

        if navigation_path == "/":
            self.redraw_file_tree()
        else:
            self.redraw_file_tree(ftp_client.get_path())

        self.current_path.update_path()

    def log_out(self):
        ftp_client.log_out()
        self.start_login_ui()

    def on_item_clicked(self, clicked_item):
        if clicked_item.is_directory:
            directory_path = clicked_item.text(0)
            self.navigate(self.current_path.directory_path + "/" + directory_path)

    def create_dir(self):
        directory_path = self.current_path.directory_path

        def on_accept():
            new_directory_name = input_dialog.get_input()
            if new_directory_name:
                formatted_path = "/" if directory_path == "/" else directory_path + "/"
                ftp_client.create_dir(formatted_path + new_directory_name)
                self.redraw_file_tree()

        input_dialog = InputDialog(
            title="Utwórz katalog", input_title="Nazwa katalogu", on_confirm=on_accept
        )
        input_dialog.show()


class FileUploadWidget(QWidget):
    def __init__(self, parent=None, redraw_file_tree=None):
        super(FileUploadWidget, self).__init__(parent)
        self.upload_button = QPushButton("Prześlij plik")
        self.select_file_dialog = None
        self.file_path = None
        self.redraw_file_tree = redraw_file_tree

    def get_file(self, current_path=None):
        self.select_file_dialog = QFileDialog()
        self.select_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.select_file_dialog.setViewMode(QFileDialog.Detail)

        remote_path = current_path if current_path == "/" else current_path + "/"

        if self.select_file_dialog.exec_():
            file_names = self.select_file_dialog.selectedFiles()
            if file_names:
                self.file_path = str(Path(file_names[0]))
                self.upload_file(remote_path)

    def upload_file(self, remote_path):
        file_name = path.basename(self.file_path)
        full_remote_path = remote_path + file_name

        progress_dialog = ProgressDialog(
            self.file_path, full_remote_path, ftp_client, self.redraw_file_tree
        )
        progress_dialog.show()


class CurrentPath(QWidget):
    def __init__(self):
        super().__init__()
        self.directory_path = ftp_client.get_path()
        self.current_path_label = QLabel(f"Aktualna ścieżka: {self.directory_path}")

    def update_path(self):
        self.directory_path = ftp_client.get_path()
        self.current_path_label.setText(f"Aktualna ścieżka: {self.directory_path}")


class NoFilesWidget(QTreeWidgetItem):
    def __init__(self, parent=None):
        super(QTreeWidgetItem, self).__init__(parent)
        self.label = QLabel("Brak plików.")
        self.is_directory = False
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            """
            font-size: 20px;
            color: #888888;
            font-weight: bold;
            padding: 5px;
            margin: 5px;
            background-color: #f0f0f0;
        """
        )


class FileItemWidget(QTreeWidgetItem):
    def __init__(self, parent=None, redraw_file_tree=None, file_data=("-", "-", "-")):
        super(QTreeWidgetItem, self).__init__(parent)
        file_icon_path = path.join(path.dirname(__file__), r"assets\file.png")
        folder_icon_path = path.join(path.dirname(__file__), r"assets\folder.png")
        file_icon = QIcon(file_icon_path)
        folder_icon = QIcon(folder_icon_path)
        button_box = QHBoxLayout()
        button_box.setContentsMargins(5, 5, 5, 5)
        button_widget = QWidget()
        button_delete = QPushButton("Usuń")
        button_download = QPushButton("Pobierz")
        button_box.addWidget(button_delete)
        button_delete.clicked.connect(self.handle_delete)
        button_widget.setLayout(button_box)
        parent.setItemWidget(self, 3, button_widget)

        self.file_name = file_data[0]
        self.file_size = file_data[1]
        self.file_date = file_data[2]

        self.is_directory = False
        self.setText(0, self.file_name)

        self.redraw_file_tree = redraw_file_tree

        # Jeżeli file_size == "-", jest to folder
        if self.file_size == "-":
            self.setIcon(0, folder_icon)
            self.setText(1, "-")
            self.setText(2, "-")
            self.is_directory = True

        else:
            self.setIcon(0, file_icon)
            self.setText(1, self.file_size)
            self.setText(2, self.file_date)
            button_box.addWidget(button_download)
            button_download.clicked.connect(
                lambda: ftp_client.download_file(self.file_name)
            )
            self.is_directory = False

    def handle_delete(self):
        if self.file_size == "-":
            ftp_client.delete_dir(self.file_name)
        else:
            ftp_client.delete_file(self.file_name)

        self.redraw_file_tree()
