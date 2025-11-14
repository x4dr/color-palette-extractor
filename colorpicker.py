from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QVBoxLayout
from PyQt5.QtGui import QColor
import sys

def show_color_boxes(hex_colors, color_changed=lambda i, color: None):
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()

    def make_handler(i, button):
        def handler():
            color = QColorDialog.getColor(QColor(hex_colors[i]))
            if color.isValid():
                hex_colors[i] = color.name()
                button.setStyleSheet(f'background-color: {hex_colors[i]}')
                color_changed(i, hex_colors[i])
        return handler

    for i, hex_color in enumerate(hex_colors):
        btn = QPushButton()
        btn.setFixedHeight(50)
        btn.setStyleSheet(f'background-color: {hex_color}')
        btn.clicked.connect(make_handler(i, btn))
        layout.addWidget(btn)

    window.setLayout(layout)
    window.show()
    app.exec_()

show_color_boxes(["#ff0000", "#00ff00", "#0000ff"])