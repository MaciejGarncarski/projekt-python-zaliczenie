from PyQt5.QtWidgets import QMessageBox

app_title = "Projekt FTP Maciej Garncarski"

default_ftp_settings = {
    "host": "ftp.maciej-garncarski.pl",
    "port": "21",
    "user": "testowy",
    "password": "test123",
}

icons = {
    "info": QMessageBox.Information,
    "warning": QMessageBox.Warning,
    "error": QMessageBox.Critical,
    "question": QMessageBox.Question,
}

dialog_width = 300
dialog_height = 100

default_ftp_settings_description = f"""Testowy serwer FTP:
  - host: {default_ftp_settings["host"]}
  - port: {default_ftp_settings["port"]}
  - użytkownik: {default_ftp_settings["user"]}
  - hasło: {default_ftp_settings["password"]}
"""

ftp_connection_errors = {
    331: "Nazwa użytkownika OK, potrzebne hasło.",
    332: "Potrzebne konto do logowania.",
    350: "Żądana akcja pliku oczekuje na dalsze informacje.",
    421: "Usługa niedostępna.",
    425: "Nie można otworzyć połączenia danych.",
    426: "Połączenie zamknięte; transfer przerwany.",
    434: "Host nieosiągalny.",
    450: "Żądana akcja pliku nie wykonana. Plik niedostępny.",
    451: "Żądana akcja przerwana: lokalny błąd w przetwarzaniu.",
    452: "Żądana akcja pliku nie wykonana. Brak miejsca na dysku.",
    500: "Błąd składni, nie rozpoznano polecenia.",
    501: "Błąd składni w parametrach lub argumentach.",
    502: "Polecenie niezaimplementowane.",
    503: "Zła kolejność poleceń.",
    504: "Polecenie niezaimplementowane dla tego parametru.",
    530: "Nieprawidłowe dane logowania.",
    532: "Potrzebne konto do przechowywania plików.",
    550: "Żądana akcja pliku nie wykonana. Plik niedostępny.",
    551: "Żądana akcja przerwana: nieznany typ strony.",
    552: "Żądana akcja pliku przerwana. Przekroczono przydział pamięci.",
    553: "Żądana akcja pliku nie wykonana. Niedozwolona nazwa pliku.",
}
