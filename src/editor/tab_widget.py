from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerSQL
from PyQt6.Qsci import QsciLexerHTML, QsciLexerMarkdown, QsciLexerJSON
from PyQt6.QtGui import QColor

class TabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.editor = QsciScintilla()
        self.setup_editor()
        
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)
        
        self.current_file = None
        self.current_lexer = None
        self.current_encoding = 'utf-8'
        self.is_modified = False
        
        self.editor.textChanged.connect(self.handle_text_changed)
        
    def setup_editor(self):
        self.editor.setUtf8(True)
        self.editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.editor.setMarginWidth(0, "000")
        self.editor.setIndentationsUseTabs(False)
        self.editor.setAutoIndent(True)
        self.editor.setIndentationGuides(True)
        self.editor.setTabWidth(4)
        margin_color = QColor(211, 211, 211)
        self.editor.setMarginsForegroundColor(margin_color)
        
    def handle_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            # 获取父标签页组件并更新标签
            parent = self.parent()
            while parent and not isinstance(parent, QTabWidget):
                parent = parent.parent()
            
            if parent:
                index = parent.indexOf(self)
                current_text = parent.tabText(index)
                if not current_text.startswith('*'):
                    parent.setTabText(index, f"*{current_text}") 