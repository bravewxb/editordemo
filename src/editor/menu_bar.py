from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence

class MenuBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.create_menu()
        
    def create_menu(self):
        menubar = self.parent.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        self.add_file_actions(file_menu)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        self.add_edit_actions(edit_menu)
        
        # 格式化菜单
        format_menu = menubar.addMenu('格式化')
        self.add_format_actions(format_menu)

    def add_file_actions(self, menu):
        new_action = QAction('新建', self.parent)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.parent.new_file)
        menu.addAction(new_action)
        
        open_action = QAction('打开', self.parent)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.parent.open_file)
        menu.addAction(open_action)
        
        save_action = QAction('保存', self.parent)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.parent.save_file)
        menu.addAction(save_action)

    def add_edit_actions(self, menu):
        goto_action = QAction('跳转到行', self.parent)
        goto_action.setShortcut('Ctrl+G')
        goto_action.triggered.connect(self.parent.goto_line)
        menu.addAction(goto_action)

    def add_format_actions(self, menu):
        format_json_action = QAction('格式化JSON', self.parent)
        format_json_action.setShortcut('Ctrl+Shift+J')
        format_json_action.triggered.connect(self.parent.format_json)
        menu.addAction(format_json_action) 