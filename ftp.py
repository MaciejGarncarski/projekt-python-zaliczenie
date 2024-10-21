from ftplib import FTP


class ReusableFTP:
    def __init__(self):
        self.ftp = None
        self.user = None
        self.host = None
        self.port = None
        self.password = None

    def connect(self, host, port, user, password):
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

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp = None
            print("Disconnected")

    def upload_file(self, file_path, remote_path):
        # self.connect(host, user, passwd)
        with open(file_path, "rb") as file:
            self.ftp.storbinary(f"STOR {remote_path}", file)
        print(f"Uploaded {file_path} to {remote_path}")
        self.disconnect()

    def download_file(self, remote_path, file_path):
        # self.connect(host, user, passwd)
        with open(file_path, "wb") as file:
            self.ftp.retrbinary(f"RETR {remote_path}", file.write)
        print(f"Downloaded {remote_path} to {file_path}")
        self.disconnect()

    def list_files(self, directory="."):
        # self.connect(host, user, passwd)
        files = self.ftp.nlst(directory)
        print(f"Files in {directory}: {files}")
        self.disconnect()
        return files

    def pwd(self):
        return self.ftp.pwd()


# Example usage
ftp_client = ReusableFTP()
