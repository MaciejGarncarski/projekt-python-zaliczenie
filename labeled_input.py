from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel

class LabeledInput(QWidget):
    def __init__(self, placeholder="Tytuł", form_box=None, is_password=False, default_text=None, parent=None):
        super().__init__(parent)

        self.label = QLabel(placeholder + ":")
        self.label.setStyleSheet("padding-right: 10px")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setMaximumSize(300, 100)

        if is_password:
            self.input_field.setEchoMode(QLineEdit.EchoMode.Password)

        if default_text:
            self.input_field.setText(default_text)

        form_box.addRow(self.label, self.input_field)

    def set_text(self, text):
        self.input_field.setText(text)

    def get_text(self):
        return self.input_field.text()