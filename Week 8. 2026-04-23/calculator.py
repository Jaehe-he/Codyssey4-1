import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
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
        self.expression_text = ''

        self.old_pos = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(420, 860)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(20, 20, 20, 20)

        self.phone_body = QFrame()
        self.phone_body.setStyleSheet(
            'QFrame {'
            'background-color: #111111;'
            'border: 4px solid #2b2b2b;'
            'border-radius: 42px;'
            '}'
        )

        phone_layout = QVBoxLayout()
        phone_layout.setContentsMargins(18, 18, 18, 22)
        phone_layout.setSpacing(10)

        self.notch = QFrame()
        self.notch.setFixedSize(170, 34)
        self.notch.setStyleSheet(
            'QFrame {'
            'background-color: black;'
            'border-radius: 17px;'
            '}'
        )

        notch_wrapper = QVBoxLayout()
        notch_wrapper.setContentsMargins(0, 0, 0, 0)
        notch_wrapper.setAlignment(Qt.AlignHCenter)
        notch_wrapper.addWidget(self.notch)

        self.history_label = QLabel('')
        self.history_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.history_label.setFixedHeight(48)
        self.history_label.setStyleSheet(
            'color: #9a9a9a;'
            'background-color: transparent;'
            'padding-right: 10px;'
        )
        self.history_label.setFont(QFont('Arial', 16))

        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.display.setFixedHeight(110)
        self.display.setStyleSheet(
            'color: white;'
            'background-color: transparent;'
            'padding-right: 10px;'
        )
        self.display.setFont(QFont('Arial', 40))

        display_wrapper = QVBoxLayout()
        display_wrapper.setContentsMargins(0, 8, 0, 8)
        display_wrapper.setSpacing(0)
        display_wrapper.addWidget(self.history_label)
        display_wrapper.addWidget(self.display)

        button_layout = QGridLayout()
        button_layout.setSpacing(12)

        buttons = [
            [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('÷', 'operator')],
            [('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator')],
            [('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator')],
            [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
            [('0', 'number_wide'), ('.', 'number'), ('=', 'operator')],
        ]

        for row, button_row in enumerate(buttons):
            col = 0
            for text, button_type in button_row:
                button = QPushButton(text)
                button.setFont(QFont('Arial', 20))
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(self.handle_button_click)

                if button_type == 'function':
                    button.setFixedSize(82, 82)
                    button.setStyleSheet(self.function_button_style())
                    button_layout.addWidget(button, row, col)
                    col += 1

                elif button_type == 'operator':
                    button.setFixedSize(82, 82)
                    button.setStyleSheet(self.operator_button_style())
                    button_layout.addWidget(button, row, col)
                    col += 1

                elif button_type == 'number':
                    button.setFixedSize(82, 82)
                    button.setStyleSheet(self.number_button_style())
                    button_layout.addWidget(button, row, col)
                    col += 1

                elif button_type == 'number_wide':
                    button.setFixedSize(176, 82)
                    button.setStyleSheet(self.zero_button_style())
                    button_layout.addWidget(button, row, col, 1, 2)
                    col += 2

        phone_layout.addLayout(notch_wrapper)
        phone_layout.addLayout(display_wrapper)
        phone_layout.addLayout(button_layout)

        self.phone_body.setLayout(phone_layout)
        outer_layout.addWidget(self.phone_body)
        self.setLayout(outer_layout)

    def number_button_style(self):
        return (
            'QPushButton {'
            'background-color: #505050;'
            'color: white;'
            'border: none;'
            'border-radius: 41px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #6a6a6a;'
            '}'
        )

    def zero_button_style(self):
        return (
            'QPushButton {'
            'background-color: #505050;'
            'color: white;'
            'border: none;'
            'border-radius: 41px;'
            'text-align: left;'
            'padding-left: 30px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #6a6a6a;'
            '}'
        )

    def function_button_style(self):
        return (
            'QPushButton {'
            'background-color: #d4d4d2;'
            'color: black;'
            'border: none;'
            'border-radius: 41px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #ebebeb;'
            '}'
        )

    def operator_button_style(self):
        return (
            'QPushButton {'
            'background-color: #ff9f0a;'
            'color: white;'
            'border: none;'
            'border-radius: 41px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #ffb340;'
            '}'
        )

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
        if self.current_input == 'Error':
            self.current_input = '0'

        if self.reset_input:
            self.current_input = number
            self.reset_input = False
            return

        if self.current_input == '0':
            self.current_input = number
        else:
            self.current_input += number

    def input_decimal(self):
        if self.current_input == 'Error':
            self.current_input = '0'

        if self.reset_input:
            self.current_input = '0.'
            self.reset_input = False
            return

        if '.' not in self.current_input:
            self.current_input += '.'

    def set_operator(self, operator):
        if self.current_input == 'Error':
            return

        if self.pending_operator is not None and not self.reset_input:
            self.calculate_result()

        try:
            self.stored_value = float(self.current_input)
        except ValueError:
            self.stored_value = 0.0

        self.pending_operator = operator
        self.expression_text = f'{self.format_number(self.stored_value)} {operator}'
        self.reset_input = True

    def calculate_result(self):
        if self.pending_operator is None or self.stored_value is None:
            return

        try:
            current_value = float(self.current_input)
        except ValueError:
            current_value = 0.0

        full_expression = (
            f'{self.format_number(self.stored_value)} '
            f'{self.pending_operator} '
            f'{self.format_number(current_value)} ='
        )

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
                    self.expression_text = full_expression
                    self.stored_value = None
                    self.pending_operator = None
                    self.reset_input = True
                    return
                result = self.stored_value / current_value
            else:
                return

            self.current_input = self.format_number(result)
            self.expression_text = full_expression
            self.stored_value = None
            self.pending_operator = None
            self.reset_input = True
        except Exception:
            self.current_input = 'Error'
            self.expression_text = full_expression
            self.stored_value = None
            self.pending_operator = None
            self.reset_input = True

    def clear_all(self):
        self.current_input = '0'
        self.stored_value = None
        self.pending_operator = None
        self.reset_input = False
        self.expression_text = ''

    def toggle_sign(self):
        if self.current_input in ['0', 'Error']:
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
        self.history_label.setText(self.expression_text)
        self.display.setText(self.current_input)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None


def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()