# Klient FTP - Projekt na zalicznie z przedmiotu "Wstęp do Programowania"

# Uruchomienie projektu
Podane komendy należy uruchomić w katalogu projektu.

## Linux/macOS lub inny system Unixowy



```bash
# Tylko raz, podczas pierwszego uruchomienia aplikacji
python3 -m venv env # tworzy środowisko wirtualne w katalogu projektu

# Za każdym razem, po ponownym uruchomieniu komputera
# aktywuje środowisko wirtualne
source env/bin/activate 

# Tylko raz, podczas pierwszego uruchomienia aplikacji
# instaluje bibliotekę do GUI
python3 -m pip install PyQt5 

# Uruchamia aplikację
python3 main.py
```

## Windows 10/11
```sh
# Tylko raz, podczas pierwszego uruchomienia aplikacji
py -m venv env # tworzy środowisko wirtualne w katalogu projektu

# Za każdym razem, po ponownym uruchomieniu komputera
# aktywuje środowisko wirtualne
env\Scripts\activate.bat 

# Tylko raz, podczas pierwszego uruchomienia aplikacji
# instaluje bibliotekę do GUI
py -m pip install PyQt5 

# Uruchamia aplikację
py main.py
```




