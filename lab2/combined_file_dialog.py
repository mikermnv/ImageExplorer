from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal

class CombinedFileDialog(QWidget):
    """Supports only single file or directory selection"""
    selected = Signal((str))

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        layout.addWidget(self.path_edit)

        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        self.browse_button = QPushButton("Browse")
        layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.filenameSelected)

    def setPath(self, path : str):
        self.file_dialog.setDirectory(path)
        self.path_edit.setText(path)

    def getPath(self) -> str:
        return self.path_edit.text()

    def clear(self):
        self.path_edit.clear()
        self.file_dialog.setDirectory(".")

    def setDisabledStatus(self, status : bool):
        self.browse_button.setDisabled(status)
        self.path_edit.setDisabled(status)

    def filenameSelected(self):
        if self.file_dialog.exec():
            self.selected_files = self.file_dialog.selectedFiles()
            files_str = ', '.join(self.selected_files)
            self.path_edit.setText(files_str)
            for file in self.selected_files:
                self.selected.emit(file)
        

