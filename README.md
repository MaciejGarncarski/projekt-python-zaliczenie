# Klient FTP - Projekt na zalicznie z przedmiotu "Wstęp do Programowania"

# Uruchomienie projektu
Podane komendy należy uruchomić w katalogu projektu. Projekt używa venv - wirtualne środowisko pythona, czyli wszystkie potrzebne biblioteki projektu nie są instalowane globalnie, a są umieszczone w jego katalogu. Po usunięciu plików projektu z komputera, usunięte zostają również wszystkie biblioteki tej aplikacji. 

## Linux/macOS lub inny system Unixowy
```bash
python3 -m pip install -r .\requirements.txt # instaluje potrzebne biblioteki, obecnie tylko PyQt6
source venv/bin/activate # aktywuje środowisko wirtualne
python3 main.py # uruchamia aplikację
```

## Windows
```sh
py -m pip install -r .\requirements.txt # instaluje potrzebne biblioteki, obecnie tylko PyQt6
.\venv\Scripts\activate # aktywuje środowisko wirtualne
py main.py # uruchamia aplikację
```
Jeżeli skrypt ".\venv\Scripts\activate" nie działa w powłoce PowerShell, należy uruchomić w cmd.





