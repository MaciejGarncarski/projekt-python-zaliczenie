from PyQt6.QtWidgets import QApplication

app_title = "Projekt FTP Maciej Garncarski"

default_ftp_settings = {
    "host": "ftp.maciej-garncarski.pl",
    "port": "21",
    "user": "testowy",
    "password": "test1223",
}

default_ftp_settings_description = f"""
Testowy serwer FTP:
  - host: {default_ftp_settings["host"]}
  - port: {default_ftp_settings["port"]}
  - użytkownik: {default_ftp_settings["user"]}
  - hasło: {default_ftp_settings["password"]}
"""

ftp_connection_errors = {
    "530": "Nieprawidłowe dane logowania.",
    "434": "Host nieosiągalny.",
}
