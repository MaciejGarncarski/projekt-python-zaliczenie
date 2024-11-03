# Klient FTP - Projekt na zalicznie z przedmiotu <br/> "Wstęp do Programowania"

---

# Autor: Maciej Garncarski, indeks: 181846

---

# Uruchamianie projektu

### Na systemie Windows można uruchomić gotowy plik exe. Należy pobrać plik `Projekt.FTP.Maciej.Garncarski.exe` z tego [linku](https://github.com/MaciejGarncarski/projekt-python-zaliczenie/releases/).

[Instrukcja budowania exe aplikacji](#4-budowanie-exe-opcjonalne)

[Znane problemy](#5-znane-problemy)

---

## 1. Pobieranie plików projektu
Pobierz [plik zip](https://codeload.github.com/MaciejGarncarski/projekt-python-zaliczenie/zip/refs/heads/master) lub sklonuj repozytorium git:

```sh
git clone https://github.com/MaciejGarncarski/projekt-python-zaliczenie.git
cd projekt-python-zaliczenie
```

## 2. Instalacja biblioteki do GUI i aktywacja środowiska wirtualnego
### Podane komendy należy uruchomić w katalogu projektu.

### Windows
```sh
py -m venv .venv
.\.venv\Scripts\activate
# lub
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
.\.venv\Scripts\activate
# lub
.\.venv\Scripts\activate.bat

py main.py
```

### Linux/macOS
```bash
source .venv/bin/activate
python3 main.py
```


## 4. Budowanie exe (opcjonalne)
Wymagane jest zainstalowanie biblioteki `pyinstaller`
### Windows
```sh
py -m pip install pyinstaller

.\.venv\Scripts\activate
# lub
.\.venv\Scripts\activate.bat

pyinstaller main.spec
```
Zbudowana aplikacja będzie znajdywać się w katalogu `dist`

## 5. Znane problemy
- Przestarzałe wersje `pip` mogą powodować błędy przy instalacji PyQt5, zalecane jest zaktualizowanie `pip`
- W programie VirtualBox aplikacja zawiesza się, gdy wybrany jest typ sieci NAT, wybranie trybu Bridge powinno rozwiązać problem
- Plik exe zbudowany na systemie Windows 10 i Windows 11 nie działa na Windows 7
