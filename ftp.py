from ftplib import FTP


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
        print(f"Reconnected to {self.host}:{self.port}")

    def connect(self, host=None, port=None, user=None, password=None):
        print(host, port, user, password)

        if self.ftp is None or not self.ftp.sock:
            self.ftp = FTP()
            self.ftp.connect(host=host, port=port)
            self.ftp.login(user=user, passwd=password)

            self.host = host
            self.user = user
            self.password = password
            self.port = port

            print(f"Connected to {host}:{port}")

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
            print("Disconnected")

    def upload_file(self, file_path, remote_path, callback):
        self.reconnect()
        with open(file_path, "rb") as file:
            self.ftp.storbinary(f"STOR {remote_path}", file, 8192, callback)
        print(f"Uploaded {file_path} to {remote_path}")
        self.disconnect()

    def download_file(self, remote_path, file_path):
        self.reconnect()
        with open(file_path, "wb") as file:
            self.ftp.retrbinary(f"RETR {remote_path}", file.write)
        print(f"Downloaded {remote_path} to {file_path}")
        self.disconnect()

    def list_files(self, directory="."):
        self.reconnect()
        files = self.ftp.nlst(directory)
        print(f"Files in {directory}: {files}")
        self.disconnect()
        return files

    def get_path(self):
        return self.ftp.pwd()


ftp_client = ReusableFTP()
