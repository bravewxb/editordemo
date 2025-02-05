from PyQt6.QtWidgets import QTabWidget, QMessageBox
from .tab_widget import TabWidget
import os

class EditorTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        
    def new_tab(self):
        tab = TabWidget(self)
        index = self.addTab(tab, "未命名")
        self.setCurrentIndex(index)
        return tab
        
    def close_tab(self, index):
        tab = self.widget(index)
        if tab.is_modified:
            reply = QMessageBox.question(
                self, 
                '保存修改', 
                '文件已被修改，是否保存？',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.setCurrentIndex(index)
                tab.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        if self.count() > 1:
            self.removeTab(index)
        else:
            self.new_tab()
            self.removeTab(index) 