import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.current_input = '0'
        self.stored_value = None
        self.pending_operator = None
        self.reset_input = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(360, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        display_layout = QHBoxLayout()
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(120)
        self.display.setStyleSheet(
            'background-color: black;'
            'color: white;'
            'padding: 20px;'
            'border-radius: 10px;'
        )
        self.display.setFont(QFont('Arial', 32))
        display_layout.addWidget(self.display)

        button_layout = QGridLayout()
        button_layout.setSpacing(10)

        buttons = [
            [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('÷', 'operator')],
            [('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator')],
            [('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator')],
            [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
            [('0', 'number'), ('.', 'number'), ('=', 'operator')],
        ]

        for row, button_row in enumerate(buttons):
            col = 0
            for text, button_type in button_row:
                button = QPushButton(text)
                button.setFixedHeight(80)
                button.setFont(QFont('Arial', 20))
                button.clicked.connect(self.handle_button_click)

                if button_type == 'number':
                    button.setStyleSheet(
                        'background-color: #505050;'
                        'color: white;'
                        'border: none;'
                        'border-radius: 40px;'
                    )
                elif button_type == 'operator':
                    button.setStyleSheet(
                        'background-color: #ff9500;'
                        'color: white;'
                        'border: none;'
                        'border-radius: 40px;'
                    )
                else:
                    button.setStyleSheet(
                        'background-color: #d4d4d2;'
                        'color: black;'
                        'border: none;'
                        'border-radius: 40px;'
                    )

                if text == '0':
                    button_layout.addWidget(button, row, col, 1, 2)
                    button.setStyleSheet(
                        'background-color: #505050;'
                        'color: white;'
                        'border: none;'
                        'border-radius: 40px;'
                        'text-align: left;'
                        'padding-left: 30px;'
                    )
                    col += 2
                else:
                    button_layout.addWidget(button, row, col)
                    col += 1

            if row == 4:
                button_layout.setColumnStretch(0, 1)
                button_layout.setColumnStretch(1, 1)
                button_layout.setColumnStretch(2, 1)
                button_layout.setColumnStretch(3, 1)

        main_layout.addLayout(display_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def handle_button_click(self):
        button = self.sender()
        text = button.text()

        if text.isdigit():
            self.input_number(text)
        elif text == '.':
            self.input_decimal()
        elif text in ['+', '-', '×', '÷']:
            self.set_operator(text)
        elif text == '=':
            self.calculate_result()
        elif text == 'AC':
            self.clear_all()
        elif text == '+/-':
            self.toggle_sign()
        elif text == '%':
            self.apply_percent()

        self.update_display()

    def input_number(self, number):
        if self.reset_input:
            self.current_input = number
            self.reset_input = False
            return

        if self.current_input == '0':
            self.current_input = number
        else:
            self.current_input += number

    def input_decimal(self):
        if self.reset_input:
            self.current_input = '0.'
            self.reset_input = False
            return

        if '.' not in self.current_input:
            self.current_input += '.'

    def set_operator(self, operator):
        if self.pending_operator is not None and not self.reset_input:
            self.calculate_result()

        try:
            self.stored_value = float(self.current_input)
        except ValueError:
            self.stored_value = 0.0

        self.pending_operator = operator
        self.reset_input = True

    def calculate_result(self):
        if self.pending_operator is None or self.stored_value is None:
            return

        try:
            current_value = float(self.current_input)
        except ValueError:
            current_value = 0.0

        try:
            if self.pending_operator == '+':
                result = self.stored_value + current_value
            elif self.pending_operator == '-':
                result = self.stored_value - current_value
            elif self.pending_operator == '×':
                result = self.stored_value * current_value
            elif self.pending_operator == '÷':
                if current_value == 0:
                    self.current_input = 'Error'
                    self.stored_value = None
                    self.pending_operator = None
                    self.reset_input = True
                    return
                result = self.stored_value / current_value
            else:
                return

            self.current_input = self.format_number(result)
            self.stored_value = None
            self.pending_operator = None
            self.reset_input = True
        except Exception:
            self.current_input = 'Error'
            self.stored_value = None
            self.pending_operator = None
            self.reset_input = True

    def clear_all(self):
        self.current_input = '0'
        self.stored_value = None
        self.pending_operator = None
        self.reset_input = False

    def toggle_sign(self):
        if self.current_input == '0' or self.current_input == 'Error':
            return

        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = '-' + self.current_input

    def apply_percent(self):
        if self.current_input == 'Error':
            return

        try:
            value = float(self.current_input) / 100
            self.current_input = self.format_number(value)
        except ValueError:
            self.current_input = 'Error'
            self.reset_input = True

    def format_number(self, value):
        if value == int(value):
            return str(int(value))
        return str(value)

    def update_display(self):
        self.display.setText(self.current_input)


def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()