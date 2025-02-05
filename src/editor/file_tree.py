from PyQt6.QtWidgets import QTreeView, QMenu
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QDir

class FileTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(200)
        
        # 创建标准项模型
        self.file_model = QStandardItemModel()
        self.file_model.setHorizontalHeaderLabels(['文件'])
        
        # 设置模型到树视图
        self.setModel(self.file_model)
        
        # 添加根目录
        self.populate_tree(QDir.currentPath(), self.file_model.invisibleRootItem())
        
        # 创建上下文菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def populate_tree(self, path, parent_item):
        directory = QDir(path)
        directory.setFilter(QDir.Filter.NoDotAndDotDot | 
                          QDir.Filter.AllDirs | 
                          QDir.Filter.Files)
        
        for entry in directory.entryInfoList():
            item = QStandardItem(entry.fileName())
            item.setData(entry.filePath(), Qt.ItemDataRole.UserRole)
            
            if entry.isDir():
                self.populate_tree(entry.filePath(), item)
            
            parent_item.appendRow(item)

    def set_root_directory(self, path):
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['文件'])
        self.populate_tree(path, self.file_model.invisibleRootItem()) 