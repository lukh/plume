from PySide import QtWidgets, QtCore

from PySide.QtWidgets import QDialog, QGridLayout, QListWidget, QPushButton, QFileDialog, QDialogButtonBox, QListWidgetItem, QCheckBox, QTextEdit, QLabel
from PySide.QtGui import QBrush, QColorConstants, QColor

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




class CommitListWidget(QListWidget):
    COLOR_MAP = {
        "modified": QColor("#0066cc"),
        "added": QColor("#009900"),
        "deleted": QColor("#cc0000"),
        "conflicted": QColor("#ff6600"),
        "missing": QColor("#990099"),
        "unversioned": QColor("#808080"),
    }

    def addFile(self, path, status):
        item = QListWidgetItem(path)
        item.setCheckState(QtCore.Qt.Unchecked)
        if status in self.COLOR_MAP:
            item.setForeground(QBrush(self.COLOR_MAP[status]))
        self.addItem(item)

    def getSelectedPaths(self):
        return [self.item(x).text() for x in range(self.count()) if self.item(x).checkState() == QtCore.Qt.Checked]


class CommitDialog(QDialog):
    def __init__(self, paths, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('SVN Commit')

        layout = QGridLayout(self)
        self.setLayout(layout)

        self.list_widget = CommitListWidget(self)
        for s, p in paths:
            self.list_widget.addFile(p, s)

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
        paths_to_commit = self.list_widget.getSelectedPaths()

        if commit_msg == "" or len(paths_to_commit) == 0:
            return False

        super().accept()

    @staticmethod
    def get_commit_infos(paths):
        dialog = CommitDialog(paths)
        retcode = dialog.exec_()

        paths_to_commit = dialog.list_widget.getSelectedPaths()
        commit_msg = dialog.text_edit.toPlainText()

        return retcode == 1, paths_to_commit, commit_msg



def open_or_create_directory(log_dir, caption=""):
    """
    open or create a directory
    """

    dialog = QtWidgets.QFileDialog(None, caption=caption)
    dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    dialog.setDirectory(log_dir)
    dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
    dialog.setLabelText(QtWidgets.QFileDialog.Accept, "Select")
    if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
        directories = dialog.selectedFiles()
        if len(directories) != 1:
            raise ValueError("can't get more than one dir selected")

        return directories[0]

    return None