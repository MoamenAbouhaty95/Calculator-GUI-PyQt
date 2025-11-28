#!/usr/bin/env python3
"""
Simple but robust calculator using PyQt5.
Features:
- Basic arithmetic: + - * / % **
- Parentheses and decimal numbers
- Clear, Backspace, Equals
- Keyboard input (numbers, operators, Enter, Backspace)
- Safe evaluation using ast (no eval on raw input)

Run:
pip install PyQt5
python pyqt_calculator.py
"""

import sys
import ast
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt


class SafeEvaluator(ast.NodeVisitor):
    """Safely evaluate arithmetic expressions using AST."""

    ALLOWED_BINOPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a ** b,
        ast.Mod: lambda a, b: a % b,
        ast.FloorDiv: lambda a, b: a // b,
    }

    ALLOWED_UNARYOPS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)

        elif isinstance(node, ast.BinOp):
            return self.visit_BinOp(node)

        elif isinstance(node, ast.UnaryOp):
            return self.visit_UnaryOp(node)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Invalid constant")

        elif hasattr(ast, "Num") and isinstance(node, ast.Num):
            return node.n

        else:
            raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in self.ALLOWED_BINOPS:
            try:
                return self.ALLOWED_BINOPS[op_type](left, right)
            except ZeroDivisionError:
                raise
        raise ValueError(f"Operator {op_type.__name__} not allowed")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in self.ALLOWED_UNARYOPS:
            return self.ALLOWED_UNARYOPS[op_type](operand)
        raise ValueError(f"Unary operator {op_type.__name__} not allowed")


def safe_eval(expr: str):
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError("Syntax error")
    evaluator = SafeEvaluator()
    return evaluator.visit(tree)


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Calculator")
        self.setFixedSize(360, 480)

        self._central = QWidget(self)
        self.setCentralWidget(self._central)

        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLineEdit {
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                padding: 8px;
                background: #2d2d2d;
                color: white;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #ffffff;
                font-size: 16px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #6c6c6c; }
        """)

        self.main_layout = QVBoxLayout()
        self._central.setLayout(self.main_layout)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(False)
        self.display.setFixedHeight(60)
        font = self.display.font()
        font.setPointSize(18)
        self.display.setFont(font)
        self.main_layout.addWidget(self.display)

        self.create_buttons()

    def create_buttons(self):
        buttons = [
            ['C', '/', '%', '⌫'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '='],
        ]

        grid = QGridLayout()
        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                btn = QPushButton(label)
                btn.setFixedSize(80, 60)
                btn.clicked.connect(self.on_button_clicked)
                grid.addWidget(btn, r, c)

        self.main_layout.addLayout(grid)

    def on_button_clicked(self):
        sender = self.sender()
        text = sender.text()
        if text == 'C':
            self.display.clear()
        elif text == '⌫':
            self.display.setText(self.display.text()[:-1])
        elif text == '=':
            self.calculate()
        elif text == '±':
            self.toggle_sign()
        elif text == '%':
            try:
                cur = self.display.text()
                if cur:
                    val = safe_eval(cur)
                    self.display.setText(str(val / 100))
            except Exception:
                self.display.setText('Error')
        else:
            self.display.setText(self.display.text() + text)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.calculate()
            return
        elif key == Qt.Key_Backspace:
            self.display.setText(self.display.text()[:-1])
            return
        elif key == Qt.Key_Escape:
            self.display.clear()
            return

        ch = event.text()
        allowed = '0123456789.+-*/()%'
        if ch in allowed:
            self.display.setText(self.display.text() + ch)

    def toggle_sign(self):
        cur = self.display.text()
        if cur:
            try:
                val = safe_eval(cur)
                self.display.setText(str(-val))
            except Exception:
                self.display.setText('Error')

    def calculate(self):
        expr = self.display.text()
        if not expr:
            return
        try:
            result = safe_eval(expr)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.display.setText(str(result))
        except ZeroDivisionError:
            self.display.setText('Division by zero')
        except Exception:
            self.display.setText('Error')


def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()