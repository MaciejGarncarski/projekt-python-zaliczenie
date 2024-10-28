from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox

from constants import icons


class ConfirmationBox(QMessageBox):
    def __init__(
        self,
        title="Potwierdź",
        text=None,
        button_yes_text="Potwierdź",
        button_no_text="Anuluj",
        on_confirm=None,
    ):
        super().__init__()
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button_yes = self.button(QMessageBox.Yes)
        button_yes.setText(button_yes_text)
        button_no = self.button(QMessageBox.No)
        button_no.setText(button_no_text)
        self.setDefaultButton(QMessageBox.No)
        self.on_confirm = on_confirm

    def show(self):
        result = self.exec_()

        if result == QMessageBox.No:
            self.close()

        if result == QMessageBox.Yes:
            self.on_confirm()


class NotificationBox(QMessageBox):
    def __init__(self, text=None, icon="info"):
        super().__init__()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.icon = icon
        self.text = text
        self.setFixedSize(300, 100)

    def show(self):
        self.setWindowTitle("Powiadomienie")
        self.setText(self.text or "Powiadomienie")
        self.setIcon(icons.get(self.icon) or icons.get("info"))
        self.setModal(True)
        self.setStandardButtons(QMessageBox.Yes)
        button_yes = self.button(QMessageBox.Yes)
        button_yes.setText("Ok")

        result = self.exec_()

        if result == QMessageBox.Yes:
            self.close()
