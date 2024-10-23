from ftplib import FTP
from utils import is_directory, convert_size


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
        print('upload')

    def download_file(self, remote_path, file_path):
        with open(file_path, "wb") as file:
            self.ftp.retrbinary(f"RETR {remote_path}", file.write)

    def list_files(self, directory="."):
        files = self.ftp.nlst(directory)
        file_list = []

        for file_name in files:
            formatted_file_name = file_name if directory is '.' else file_name.replace(directory + "/", '', 1)

            if is_directory(self.ftp, file_name):
                file_list.append((formatted_file_name, '-', '-'))
                continue

            self.ftp.sendcmd("TYPE i")
            timestamp = self.ftp.voidcmd(f"MDTM {file_name}")[4:].strip()
            year = timestamp[:4]
            month = timestamp[4:6]
            day = timestamp[6:8]
            hour = timestamp[8:10]
            minute = timestamp[10:12]
            second = timestamp[12:14]
            file_date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
            file_size_bytes = self.ftp.size(file_name)
            file_formatted_size = convert_size(file_size_bytes)
            file_data = (formatted_file_name, file_formatted_size, file_date)
            file_list.append(file_data)

        return file_list

    def cwd(self, path):
        self.ftp.cwd(path)

    def get_path(self):
        return self.ftp.pwd()


ftp_client = ReusableFTP()
