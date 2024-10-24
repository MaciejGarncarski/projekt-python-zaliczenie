from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem, QPushButton, QFileDialog, QWidget, QProgressDialog, QLabel, QHBoxLayout

class FileItemWidget(QTreeWidgetItem):
    def __init__(self, parent=None, delete_file=None, download_file=None, delete_dir=None, file_name=None, file_size=None, file_date=None):
        super(QTreeWidgetItem, self).__init__(parent)
        file_icon = QIcon("file.png")
        folder_icon = QIcon("folder.png")
        self.is_directory = False
        self.setText(0, file_name)
        button_widget = QWidget()
        button_box = QHBoxLayout()
        button_delete = QPushButton("Usuń")
        button_download = QPushButton("Pobierz")

        button_box.setContentsMargins(5, 5, 5, 5)
        button_widget.setLayout(button_box)

        # Jeżeli file_size == '-', jest to folder
        if file_size == "-":
            def handle_delete_dir():
                delete_dir(file_name)
                parent.parent().show_file_tree()

            self.setIcon(0, folder_icon)
            self.setText(1, "-")
            self.setText(2, "-")
            button_box.addWidget(button_delete)
            button_delete.clicked.connect(handle_delete_dir)
            parent.setItemWidget(self, 3, button_widget)
            self.is_directory = True

        else:
            def handle_delete_file():
                delete_file(file_name)
                parent.parent().show_file_tree()

            self.setIcon(0, file_icon)
            self.setText(1, file_size)
            self.setText(2, file_date)
            button_box.addWidget(button_delete)
            button_box.addWidget(button_download)
            button_delete.clicked.connect(handle_delete_file)
            button_download.clicked.connect(lambda: download_file(file_name))
            parent.setItemWidget(self, 3, button_widget)
            self.is_directory = False