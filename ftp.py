from ftplib import FTP, error_perm, error_temp, error_reply, error_proto
import socket

from PyQt5.QtWidgets import QFileDialog

from dialog import NotificationBox, ConfirmationBox
from ftp_widgets import FileItemWidget
from utils import is_directory, convert_size
from datetime import  datetime
import time

class ReusableFTP:
    def __init__(self):
        self.ftp = None
        self.user = None
        self.host = None
        self.port = None
        self.password = None

    def connect(self, host=None, port=None, user=None, password=None):
        if self.ftp is None or not self.ftp.sock:
            self.ftp = FTP(timeout=10)
            self.ftp.connect(host=host, port=port)
            self.ftp.login(user=user, passwd=password)
            self.host = host
            self.user = user
            self.password = password
            self.port = port

    def reconnect(self):
        try:
            self.ftp.voidcmd("NOOP")
        except (error_temp, error_perm, error_proto, error_reply, socket.timeout):
            self.ftp.connect(host=self.host, port=self.port)
            self.ftp.login(user=self.user, passwd=self.password)

    def log_out(self):
        if self.ftp:
            self.ftp = None
            self.ftp = None
            self.user = None
            self.host = None
            self.port = None
            self.password = None

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp = None

    def create_dir(self, remote_path):
        try:
            self.reconnect()
            self.ftp.mkd(remote_path)
            create_dir_notification = NotificationBox(
                text=f"Stworzono katalog {remote_path}",
                icon="info"
            )
            create_dir_notification.show()
        except error_perm:
            error_notification = NotificationBox(
                text=f"Nie udało się utworzyć katalogu {remote_path}.",
                icon="error"
            )
            error_notification.show()

    def delete_dir(self, remote_path):
        def delete():
            try:
                self.reconnect()
                self.ftp.rmd(remote_path)
                delete_dir_notification = NotificationBox(
                    text=f"Usunięto katalog {remote_path}",
                    icon="info"
                )
                delete_dir_notification.show()

            except error_perm as e:
                print(e)
                error_notification = NotificationBox(
                    text=f"Nie udało się usunąć katalogu {remote_path}.\nUsuń jego zawartość ręcznie, a następnie spróbuj ponownie.",
                    icon="error"
                )
                error_notification.show()

        delete_confirmation = ConfirmationBox(
            text=f"Usuń katalog {remote_path}",
            title="Usuń katalog",
            on_confirm=delete
        )
        delete_confirmation.show()

    def upload_file(self, file_path, remote_path, callback):
        self.reconnect()
        with open(file_path, "rb") as file:
            self.ftp.storbinary(f"STOR {remote_path}", file, 8192, callback)

        upload_notification = NotificationBox(
            text=f"Przesłano plik {file_path}",
            icon="info"
        )
        upload_notification.show()

    def download_file(self, remote_path):
        self.reconnect()

        save_path, _ = QFileDialog.getSaveFileName(None, "Zapisz plik", remote_path)

        if save_path:
            with open(save_path, 'wb') as local_file:
                self.ftp.retrbinary(f"RETR {remote_path}", local_file.write)
                download_notification = NotificationBox(
                    text=f"Pobrano plik {remote_path} do folderu {save_path}",
                    icon="info"
                )
                download_notification.show()

    def delete_file(self, remote_path):
        def delete():
            self.reconnect()
            try:
                self.ftp.delete(remote_path)
            except Exception as e:
                error_notification = NotificationBox(
                    text="Usuwanie pliku nie powiodło się.",
                    icon="error"
                )
                error_notification.show()

        delete_confirmation = ConfirmationBox(
            text=f"Usuń plik {remote_path}",
            title="Usuń plik",
            on_confirm=delete
        )
        delete_confirmation.show()


    def list_files(self, directory=".", file_tree=None):
        self.reconnect()
        files = self.ftp.nlst(directory)
        file_list = []

        for file_name in files:
            formatted_file_name = (
                file_name
                if directory == "."
                else file_name.replace(directory + "/", "", 1)
            )

            if is_directory(self.ftp, file_name):
                file_list.append(FileItemWidget(file_tree, self.delete_file, self.download_file, self.delete_dir, formatted_file_name, '-', '-'))
                continue

            file_size_bytes = self.ftp.size(file_name)
            modified_time = self.ftp.voidcmd(f"MDTM {file_name}")
            file_formatted_size = convert_size(file_size_bytes)
            modified_time = str(datetime.strptime(modified_time[4:], "%Y%m%d%H%M%S"))
            file_item = FileItemWidget(file_tree, self.delete_file, self.download_file, self.delete_dir, formatted_file_name, file_formatted_size, modified_time)
            file_list.append(file_item)

        return file_list

    def cwd(self, path):
        self.reconnect()
        self.ftp.cwd(path)

    def get_path(self):
        self.reconnect()
        return self.ftp.pwd()


ftp_client = ReusableFTP()
