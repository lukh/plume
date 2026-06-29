import os
from PySide import QtWidgets, QtCore

from PySide6.QtCore import QModelIndex
from PySide.QtWidgets import QDialog, QGridLayout, QComboBox, QListWidget, QPushButton, QFileDialog, QDialogButtonBox, QListWidgetItem, QCheckBox, QTextEdit, QLabel,  QWidget, QTreeView, QListView, QVBoxLayout, QHBoxLayout
from PySide.QtGui import QBrush, QColorConstants, QColor, QIcon

import FreeCAD as App

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.svnfilesystemmodel import SVNFileSystemModel
from freecad.plume.utils.selector import PlumeSelection

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
        paths = [self.list_widget.item(x).text() for x in range(self.list_widget.count())]

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        param.SetString("WorkingCopy Available Paths", ";".join(paths))
        # param.SetString("CurrentWorkingCopy", selected_path)

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



class DeselectableTreeView(QTreeView):
    def mousePressEvent(self, event):
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = SVNFileSystemModel()

        self.tree = DeselectableTreeView()
        self.tree.setModel(self.model)
        self.tree.selectionModel().selectionChanged.connect(self.onTreeSelectionChanged)
        self.tree.doubleClicked.connect(self.onTreeItemDoubleClicked)


        self.workingcopies_combobox = QComboBox()
        self.refreshWorkingCopies()
        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        self.workingcopies_combobox.activated.connect(lambda index : self.setRootDir(self.workingcopies_combobox.currentText()))
        if not param.IsEmpty():
            curr_wc = param.GetString("CurrentWorkingCopy")
            if curr_wc:
                index = self.workingcopies_combobox.findText(curr_wc)
                if curr_wc != -1:
                    self.workingcopies_combobox.setCurrentIndex(index)
                    self.setRootDir(curr_wc)


        menu_layout = QHBoxLayout()
        menu_layout.addWidget(self.workingcopies_combobox)
        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)

        l = QVBoxLayout()
        l.addWidget(menu_widget)
        l.addWidget(self.tree)

        self.setLayout(l)

    def onClose(self): # TODO
        PlumeSelection.instance().resetTreeSelection()
        
    def refreshWorkingCopies(self):
        self.workingcopies_combobox.clear()

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wcp = param.GetString("WorkingCopy Available Paths").split(';')

        self.workingcopies_combobox.addItems(wcp)
        PlumeSelection.instance().resetTreeSelection()

    def setRootDir(self, path):
        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if param.IsEmpty() or (param.GetString("CurrentWorkingCopy") != path):
            param.SetString("CurrentWorkingCopy", path)

        root_index = self.model.setRootPath(path)
        self.tree.setRootIndex(root_index)
        PlumeSelection.instance().resetTreeSelection()

    def onTreeSelectionChanged(self, selected, deselected):
        selector = PlumeSelection.instance()

        indexes = selected.indexes()
        if len(indexes) == 0:
            selector.resetTreeSelection()
        else:
            path = self.model.filePath(indexes[0])
            selector.setTreeSelection([path])


        # if current_index is None:
        # else:

    def refresh(self):
        root_path = self.model.rootPath()
        PlumeSelection.instance().resetTreeSelection()
        # TODO

        # for s in ps.status(".", verbose=True):
        #     self.model.setSVNInfo(s)

    def onTreeItemDoubleClicked(self, index):
        path = self.model.filePath(index)

        App.openDocument(path)


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