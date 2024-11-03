# Klient FTP - Projekt na zalicznie z przedmiotu <br/> "Wstęp do Programowania"

---

# Autor: Maciej Garncarski
# Indeks: 181846

---

# Uruchamianie projektu

##  Jeżeli używasz systemu Windows, możesz pominąć poniższe kroki i uruchomić zbudowany plik EXE. Należy pobrać plik "Projekt.FTP.Maciej.Garncarski.exe" z tego linku https://github.com/MaciejGarncarski/projekt-python-zaliczenie/releases/ 

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
# lub
.\.venv\Scripts\activate

py main.py
```

### Linux/macOS
```bash
source .venv/bin/activate
python3 main.py
```


## 4. Budowanie exe (opcjonalne)
Wymagane jest zainstalowanie biblioteki pyinstaller
### Windows
```sh
py -m pip install pyinstaller

.\.venv\Scripts\activate.bat
# lub
.\.venv\Scripts\activate

pyinstaller main.spec
```
Zbudowana aplikacja będzie znajdywać się w katalogu dist