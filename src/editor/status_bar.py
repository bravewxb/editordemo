from PyQt6.QtWidgets import QLabel, QMenu
from PyQt6.QtCore import Qt

class StatusBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.setup_status_bar()
        
    def setup_status_bar(self):
        self.status_bar = self.parent.statusBar()
        
        self.cursor_position_label = QLabel("行: 1, 列: 1")
        self.line_length_label = QLabel("字符数: 0")
        self.encoding_label = QLabel("编码: UTF-8")
        
        self.encoding_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.encoding_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.encoding_label.mousePressEvent = self.show_encoding_menu
        
        self.status_bar.addPermanentWidget(self.cursor_position_label)
        self.status_bar.addPermanentWidget(self.line_length_label)
        self.status_bar.addPermanentWidget(self.encoding_label)

    def show_encoding_menu(self, event):
        self.parent.show_encoding_menu(event)

    def update_cursor_position_label(self, text):
        self.cursor_position_label.setText(text)

    def update_line_length_label(self, text):
        self.line_length_label.setText(text)

    def update_encoding_label(self, text):
        self.encoding_label.setText(f"编码: {text}") 