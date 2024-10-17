import sys
from PyQt6.Wigets import QWindow, QApplication, QIcon

app = QApplication(sys.argv)

app_title = "Projekt FTP Maciej Garncarski"

window = QWindow()
window.setWindowTitle(app_title)
window.setWindowIcon(QIcon('icon.png'))
window.setFixedSize(800, 600)
window.show()

# Jeśli jest głównym plikiem, to wykonaj program
if __name__ == '__main__':
    sys.exit(window.exec())