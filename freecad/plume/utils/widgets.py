from PySide import QtWidgets, QtCore

from PySide.QtWidgets import QDialog, QGridLayout, QListWidget, QPushButton, QFileDialog, QDialogButtonBox

import FreeCAD as App


class ManageSubversionWorkingCopiesDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wcp = param.GetString("WorkingCopy Paths").split(';')

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


        self._selected_path = None

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

        self._selected_path = curr_item.text()

        paths = [self.list_widget.item(x).text() for x in range(self.list_widget.count())]

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        param.SetString("WorkingCopy Paths", ";".join(paths))

        return super().accept()

    def get_selected_path(self):
        return self._selected_path