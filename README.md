# Klient FTP - Projekt na zalicznie z przedmiotu <br/> "Wstęp do Programowania"

---

# Uruchamianie projektu

## Podane komendy należy uruchomić w katalogu projektu.

## 1. Pobieranie plików projektu: https://codeload.github.com/MaciejGarncarski/projekt-python-zaliczenie/zip/refs/heads/master lub sklonowanie repozytorium git

## 2. Instalacja biblioteki do GUI i aktywacja środowiska wirtualnego

### Windows
```sh
py -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
py -m pip install PyQt5 
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install PyQt5
```

## 3. Uruchomienie aplikacji
### Windows
```sh
.\.venv\Scripts\activate.bat
py main.py
```

### Linux/macOS
```bash
source .venv/bin/activate
python3 main.py
```