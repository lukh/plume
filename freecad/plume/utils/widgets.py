from PySide import QtWidgets, QtCore

from PySide.QtWidgets import QDialog, QGridLayout, QListWidget, QPushButton, QFileDialog, QDialogButtonBox, QListWidgetItem, QCheckBox, QTextEdit, QLabel
from PySide.QtGui import QBrush, QColorConstants

import FreeCAD as App


class ManageSubversionWorkingCopiesDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wcp = param.GetString("WorkingCopy Available Paths").split(';')

        self.setWindowTitle('SVN Working Copies')
        # self.setWindowIcon(QIcon('./assets/wishlist.png'))
        # self.setGeometry(100, 100, 400, 100)

        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = QListWidget(self)
        self.list_widget.addItems(wcp)
        layout.addWidget(self.list_widget, 0, 0, 4, 1)

        # create buttons
        add_button = QPushButton('Add')
        add_button.clicked.connect(self.add)

        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(self.remove)

        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear)

        layout.addWidget(add_button, 0, 1)
        layout.addWidget(remove_button, 2, 1)
        layout.addWidget(clear_button, 3, 1)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(buttonBox, 4, 0)

        # show the window
        self.show()

    def add(self):
        text = QFileDialog.getExistingDirectory(None, "Select Directory", "")
        if text:
            self.list_widget.addItem(text)

    def remove(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            current_item = self.list_widget.takeItem(current_row)
            del current_item

    def clear(self):
        self.list_widget.clear()

    def accept(self):
        curr_item = self.list_widget.currentItem()
        if curr_item is None:
            return False

        selected_path = curr_item.text()

        paths = [self.list_widget.item(x).text() for x in range(self.list_widget.count())]

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        param.SetString("WorkingCopy Available Paths", ";".join(paths))
        param.SetString("CurrentWorkingCopy", selected_path)

        return super().accept()



class CommitDialog(QDialog):
    COLOR_MAP = {
        "unversioned":QColorConstants.Blue,
        "modified":QColorConstants.Red,
    }

    def __init__(self, paths, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('SVN Commit')

        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = QListWidget(self)
        for s, p in paths:
            item = QListWidgetItem(p)
            item.setCheckState(QtCore.Qt.Unchecked)
            if s in self.COLOR_MAP:
                item.setForeground(QBrush(self.COLOR_MAP[s]))
            self.list_widget.addItem(item)

        layout.addWidget(QLabel('Files to commit', self), 0, 0)
        layout.addWidget(self.list_widget, 1, 0)

        layout.addWidget(QLabel('Commit Message', self), 2, 0)
        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit, 3, 0)


        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(buttonBox, 4, 0)

    def accept(self):
        commit_msg = self.text_edit.toPlainText()
        paths_to_commit = [self.list_widget.item(x).text() for x in range(self.list_widget.count()) if self.list_widget.item(x).checkState() == QtCore.Qt.Checked]

        if commit_msg == "" or len(paths_to_commit) == 0:
            return False

        super().accept()

    @staticmethod
    def get_commit_infos(paths):
        dialog = CommitDialog(paths)
        retcode = dialog.exec_()

        paths_to_commit = [dialog.list_widget.item(x).text() for x in range(dialog.list_widget.count()) if dialog.list_widget.item(x).checkState() == QtCore.Qt.Checked]
        commit_msg = dialog.text_edit.toPlainText()

        return retcode == 1, paths_to_commit, commit_msg