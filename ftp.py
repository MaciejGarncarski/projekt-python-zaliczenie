from ftplib import FTP
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

    def reconnect(self):
        self.ftp = FTP()
        self.ftp.connect(host=self.host, port=self.port)
        self.ftp.login(user=self.user, passwd=self.password)

    def connect(self, host=None, port=None, user=None, password=None):
        if self.ftp is None or not self.ftp.sock:
            self.ftp = FTP()
            self.ftp.connect(host=host, port=port)
            self.ftp.login(user=user, passwd=password)

            self.host = host
            self.user = user
            self.password = password
            self.port = port

    def sign_out(self):
        if self.ftp:
            self.ftp.quit()
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

    def upload_file(self, file_path, remote_path, callback):
        with open(file_path, "rb") as file:
            self.ftp.storbinary(f"STOR {remote_path}", file, 8192, callback)
        print("upload")

    def download_file(self, remote_path, file_path):
        with open(file_path, "wb") as file:
            self.ftp.retrbinary(f"RETR {remote_path}", file.write)

    def list_files(self, directory="."):
        files = self.ftp.nlst(directory)
        file_list = []

        for file_name in files:
            start = time.time()
            file_data = self.get_file_data(file_name, directory)
            file_list.append(file_data)
            end = time.time()
            print(end - start)

        return file_list

    def get_file_data(self, file_name, directory):
        formatted_file_name = (
            file_name
            if directory == "."
            else file_name.replace(directory + "/", "", 1)
        )

        if is_directory(self.ftp, file_name):
            return formatted_file_name, "-", "-"

        self.ftp.sendcmd("TYPE i")
        timestamp = self.ftp.voidcmd(f"MDTM {file_name}")[4:].strip()
        dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        file_date = datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")
        file_size_bytes = self.ftp.size(file_name)
        file_formatted_size = convert_size(file_size_bytes)
        file_data = (formatted_file_name, file_formatted_size, file_date)

        return file_data

    def cwd(self, path):
        self.ftp.cwd(path)

    def get_path(self):
        return self.ftp.pwd()


ftp_client = ReusableFTP()
