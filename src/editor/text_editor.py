import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                            QVBoxLayout, QWidget, QMessageBox, QToolBar,
                            QInputDialog, QLabel, QTabWidget,
                            QTreeView, QSplitter, QMenu)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QColor, QStandardItemModel, QStandardItem
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerSQL, QsciLexerHTML, QsciLexerMarkdown, QsciLexerJSON
import os
import json
from PyQt6.QtCore import Qt, QDir
from .editor_tab import EditorTab
from .file_tree import FileTreeView
from .menu_bar import MenuBarManager
from .status_bar import StatusBarManager

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('高级文本编辑器')
        self.setGeometry(100, 100, 1200, 600)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建文件树
        self.file_tree = FileTreeView(self)
        self.file_tree.doubleClicked.connect(self.tree_item_double_clicked)
        self.file_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        
        # 创建标签页组件
        self.tabs = EditorTab(self)
        
        # 添加组件到分割器
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        self.setCentralWidget(splitter)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建菜单栏
        self.menu_bar = MenuBarManager(self)
        
        # 创建状态栏
        self.status_bar = StatusBarManager(self)
        
        # 创建新标签页
        self.tabs.new_tab()

    def current_tab(self):
        return self.tabs.currentWidget()
        
    def current_editor(self):
        tab = self.current_tab()
        return tab.editor if tab else None

    def new_file(self):
        # 创建新的编辑器标签页
        tab = EditorTab(self)
        tab.editor.cursorPositionChanged.connect(self.update_status_bar)
        index = self.tabs.addTab(tab, "未命名")
        self.tabs.setCurrentIndex(index)
        
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开文件")
        if file_name:
            # 检查文件是否已经打开
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if tab.current_file == file_name:
                    self.tabs.setCurrentIndex(i)
                    return
                    
            try:
                # 创建新标签页
                tab = EditorTab(self)
                tab.editor.cursorPositionChanged.connect(self.update_status_bar)
                
                # 尝试不同的编码方式打开文件
                encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
                text = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        with open(file_name, 'r', encoding=encoding) as f:
                            text = f.read()
                            used_encoding = encoding
                            break
                    except UnicodeDecodeError:
                        continue
                
                if text is None:
                    raise Exception("无法检测文件编码")
                
                # 设置文本前先断开信号连接，避免触发修改标记
                tab.editor.textChanged.disconnect(tab.handle_text_changed)
                tab.editor.setText(text)
                # 重新连接信号
                tab.editor.textChanged.connect(tab.handle_text_changed)
                
                tab.current_file = file_name
                tab.current_encoding = used_encoding
                tab.is_modified = False  # 重置修改标记
                
                # 设置语法高亮
                _, file_extension = os.path.splitext(file_name)
                self.set_lexer(tab, file_extension.lower())
                
                # 添加新标签页
                index = self.tabs.addTab(tab, os.path.basename(file_name))
                self.tabs.setCurrentIndex(index)
                
                # 更新编码显示
                self.status_bar.update_encoding_label(used_encoding.upper())
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件：{str(e)}")

    def close_tab(self, index):
        tab = self.tabs.widget(index)
        if tab.is_modified:
            # 如果文件已修改，询问是否保存
            reply = QMessageBox.question(
                self, 
                '保存修改', 
                '文件已被修改，是否保存？',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                # 切换到要关闭的标签页
                self.tabs.setCurrentIndex(index)
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            # 如果是最后一个标签页，创建新的空标签页
            self.new_file()
            self.tabs.removeTab(index)

    def save_file(self):
        tab = self.current_tab()
        if not tab:
            return
            
        if not tab.current_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "保存文件")
            if file_name:
                tab.current_file = file_name
                self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_name))
            else:
                return
                
        try:
            with open(tab.current_file, 'w', encoding=tab.current_encoding) as f:
                f.write(tab.editor.text())
            # 保存成功后清除修改标记
            tab.is_modified = False
            current_index = self.tabs.currentIndex()
            current_text = self.tabs.tabText(current_index)
            if current_text.startswith('*'):
                self.tabs.setTabText(current_index, current_text[1:])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法保存文件：{str(e)}")

    def set_lexer(self, tab, file_extension):
        lexer = None
        if file_extension == '.py':
            lexer = QsciLexerPython()
        elif file_extension == '.sql':
            lexer = QsciLexerSQL()
        elif file_extension == '.md':
            lexer = QsciLexerMarkdown()
        elif file_extension in ['.html', '.htm']:
            lexer = QsciLexerHTML()
        elif file_extension == '.json':
            lexer = QsciLexerJSON()
            
        if lexer:
            tab.editor.setLexer(lexer)
            tab.current_lexer = lexer

    def update_status_bar(self):
        editor = self.current_editor()
        if not editor:
            return
            
        line, column = editor.getCursorPosition()
        self.status_bar.update_cursor_position_label(f"行: {line + 1}, 列: {column + 1}")
        
        current_line = editor.text(line)
        line_length = len(current_line)
        self.status_bar.update_line_length_label(f"字符数: {line_length}")

    def show_encoding_menu(self, event):
        # 创建编码选择菜单
        encoding_menu = QMenu(self)
        encodings = ['UTF-8', 'GBK', 'GB2312', 'ISO-8859-1']
        
        for encoding in encodings:
            action = encoding_menu.addAction(encoding)
            action.triggered.connect(lambda checked, enc=encoding: self.change_encoding(enc))
        
        # 在标签位置显示菜单
        encoding_menu.exec(self.status_bar.encoding_label.mapToGlobal(event.pos()))

    def change_encoding(self, new_encoding):
        tab = self.current_tab()
        if not tab:
            return
            
        if tab.current_file and os.path.exists(tab.current_file):
            try:
                with open(tab.current_file, 'r', encoding=new_encoding.lower()) as f:
                    text = f.read()
                
                tab.editor.setText(text)
                tab.current_encoding = new_encoding.lower()
                self.status_bar.update_encoding_label(new_encoding)
                
            except UnicodeDecodeError:
                QMessageBox.warning(self, "错误", f"无法使用 {new_encoding} 编码读取文件")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"更改编码时发生错误：{str(e)}")
        else:
            tab.current_encoding = new_encoding.lower()
            self.status_bar.update_encoding_label(new_encoding)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 添加新建文件按钮
        new_action = QAction('新建', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        # 添加打开文件按钮
        open_action = QAction('打开', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # 添加保存文件按钮
        save_action = QAction('保存', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

    def create_menu(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        # 添加跳转到行的动作
        goto_action = QAction('跳转到行', self)
        goto_action.setShortcut('Ctrl+G')
        goto_action.triggered.connect(self.goto_line)
        edit_menu.addAction(goto_action)
        
        # 格式化菜单
        format_menu = menubar.addMenu('格式化')
        
        format_json_action = QAction('格式化JSON', self)
        format_json_action.setShortcut('Ctrl+Shift+J')
        format_json_action.triggered.connect(self.format_json)
        format_menu.addAction(format_json_action)

    def goto_line(self):
        editor = self.current_editor()
        if not editor:
            return
            
        # 获取当前总行数
        total_lines = editor.lines()
        
        # 弹出输入对话框
        line_number, ok = QInputDialog.getInt(
            self, 
            "跳转到行", 
            f"输入行号 (1-{total_lines}):",
            1,  # 默认值
            1,  # 最小值
            total_lines,  # 最大值
            1  # 步长
        )
        
        if ok:
            # 跳转到指定行
            editor.setCursorPosition(line_number - 1, 0)
            # 确保该行可见
            editor.ensureLineVisible(line_number - 1)
            # 设置焦点到编辑器
            editor.setFocus()

    def format_json(self):
        editor = self.current_editor()
        if not editor:
            return
            
        try:
            # 获取当前文本
            text = editor.text()
            # 解析JSON
            parsed = json.loads(text)
            # 格式化JSON
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
            # 更新编辑器内容
            editor.setText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON格式错误", f"无法格式化JSON：{str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"格式化过程中发生错误：{str(e)}")

    def setup_file_tree(self):
        # 创建标准项模型
        self.file_model = QStandardItemModel()
        self.file_model.setHorizontalHeaderLabels(['文件'])
        
        # 设置模型到树视图
        self.file_tree.setModel(self.file_model)
        
        # 添加根目录
        self.populate_tree(QDir.currentPath(), self.file_model.invisibleRootItem())
        
        # 连接双击信号
        self.file_tree.doubleClicked.connect(self.tree_item_double_clicked)
        
        # 创建上下文菜单
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_tree_context_menu)

    def populate_tree(self, path, parent_item):
        directory = QDir(path)
        # 设置过滤器
        directory.setFilter(QDir.Filter.NoDotAndDotDot | 
                          QDir.Filter.AllDirs | 
                          QDir.Filter.Files)
        
        # 获取目录和文件列表
        for entry in directory.entryInfoList():
            item = QStandardItem(entry.fileName())
            item.setData(entry.filePath(), Qt.ItemDataRole.UserRole)
            
            if entry.isDir():
                # 如果是目录，递归添加子项
                self.populate_tree(entry.filePath(), item)
            
            parent_item.appendRow(item)

    def tree_item_double_clicked(self, index):
        # 获取文件路径
        item = self.file_model.itemFromIndex(index)
        file_path = item.data(Qt.ItemDataRole.UserRole)
        
        if os.path.isfile(file_path):
            # 检查文件是否已经打开
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if tab.current_file == file_path:
                    self.tabs.setCurrentIndex(i)
                    return
            
            # 如果文件未打开，则打开它
            self.open_specific_file(file_path)

    def show_tree_context_menu(self, position):
        # 创建上下文菜单
        context_menu = QMenu()
        
        # 获取当前选中的项
        index = self.file_tree.indexAt(position)
        if index.isValid():
            item = self.file_model.itemFromIndex(index)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            
            if os.path.isdir(file_path):
                # 目录菜单项
                set_root_action = context_menu.addAction("设为根目录")
                set_root_action.triggered.connect(lambda: self.set_root_directory(file_path))
            else:
                # 文件菜单项
                open_action = context_menu.addAction("打开")
                open_action.triggered.connect(lambda: self.tree_item_double_clicked(index))
        
        # 添加通用菜单项
        context_menu.addSeparator()
        change_root_action = context_menu.addAction("更改根目录...")
        change_root_action.triggered.connect(self.change_root_directory)
        
        # 显示菜单
        context_menu.exec(self.file_tree.viewport().mapToGlobal(position))

    def set_root_directory(self, path):
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['文件'])
        self.populate_tree(path, self.file_model.invisibleRootItem())

    def change_root_directory(self):
        new_root = QFileDialog.getExistingDirectory(self, "选择根目录", QDir.currentPath())
        if new_root:
            self.set_root_directory(new_root)

    def open_specific_file(self, file_path):
        try:
            # 创建新标签页
            tab = EditorTab(self)
            tab.editor.cursorPositionChanged.connect(self.update_status_bar)
            
            # 尝试不同的编码方式打开文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
            text = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise Exception("无法检测文件编码")
            
            # 设置文本前先断开信号连接，避免触发修改标记
            tab.editor.textChanged.disconnect(tab.handle_text_changed)
            tab.editor.setText(text)
            # 重新连接信号
            tab.editor.textChanged.connect(tab.handle_text_changed)
            
            tab.current_file = file_path
            tab.current_encoding = used_encoding
            tab.is_modified = False  # 重置修改标记
            
            # 设置语法高亮
            _, file_extension = os.path.splitext(file_path)
            self.set_lexer(tab, file_extension.lower())
            
            # 添加新标签页
            index = self.tabs.addTab(tab, os.path.basename(file_path))
            self.tabs.setCurrentIndex(index)
            
            # 更新编码显示
            self.status_bar.update_encoding_label(used_encoding.upper())
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件：{str(e)}")

def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 