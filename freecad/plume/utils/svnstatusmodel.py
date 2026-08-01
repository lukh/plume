'''
'Simple Tree Model Example' converted from C++/Qt 5 to Python 3/PyQt5.
Original example copyrighted from the Qt Company: http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
License is BSD as the original example.
'''

import os
from collections.abc import MutableMapping
from collections import OrderedDict

from PySide.QtCore    import (
   QAbstractItemModel, 
   QModelIndex, 
   Qt
)

from PySide.QtWidgets import (
    QApplication, 
    QTreeView,
)
from PySide.QtGui import QColor


from PySide.QtWidgets import QFileIconProvider
from PySide.QtCore import QFileInfo

from freecad.plume.svn.local import LocalClient, _STATUS_ENTRY


class SvnStatusItem:
    COLUMNS = [
        "filename",
        "type_raw_name",
        "revision",
        "last_committed_revision",
        "last_committed_author",
        "switched",
        "locked",
        "external"
    ]

    def __init__(self, data, parent=None):
        self._item_data = data
        self._parent_item = parent
        
        self._child_items = OrderedDict()

    def isFolder(self):
        return self._item_data.is_folder

    def path(self):
        return self._item_data.path

    def addChild(self, key, val):
        self._child_items[key] = val

    def hasChild(self, key):
        return key in self._child_items

    def getChild(self, key):
        return self._child_items[key]


    def child(self, row):
        if row < 0 or row >= len(self._child_items):
            return None
        return list(self._child_items.values())[row]


    def childCount(self):
        return len(self._child_items)

    def childNumber(self):
        if self._parent_item:
            return list(self._parent_item._child_items.values()).index(self)
        return 0

    def columnCount(self):
        return len(self.COLUMNS)

    def data(self, column):
        if not self._item_data:
        	return None
        if column < 0 or column >= self.columnCount():
            return None
        return getattr(self._item_data, self.COLUMNS[column])

    def parent(self):
        return self._parent_item
        
    def __repr__(self) -> str:
        result = f"<treeitem.SvnStatusItem at 0x{id(self):x}"
        for d in self._item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self._child_items)} children>"
        return result

class SvnStatusModel(QAbstractItemModel):
    ICON_PROVIDER = QFileIconProvider()

    STATUS_COLORS = {
        "modified": QColor("#0066cc"),
        "added": QColor("#009900"),
        "deleted": QColor("#cc0000"),
        "conflicted": QColor("#ff6600"),
        "missing": QColor("#990099"),
        "unversioned": QColor("#808080"),
    }

    def __init__(self, parent=None) :
        super().__init__(parent)

        root_data = ['Name', 'Type']
        self._root_item = SvnStatusItem(root_data)



    def _repr_recursion(self, item: SvnStatusItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        print(item)
        for child in item._child_items.values():
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self._root_item)


    def load(self, working_copy_path):
        self._wc = working_copy_path
        self._client = LocalClient(self._wc)

        self._setupModelData()

    def refresh(self):
        self._setupModelData()

    def _setupModelData(self):
        root_data = _STATUS_ENTRY(filename="FileName", type_raw_name="Type", revision="Revision", last_committed_author="Last Auth", last_committed_revision="last Revision", switched="Switched", external="External", locked="Locked")
        self._root_item = SvnStatusItem(root_data)


        tree = self._root_item

        for l in self._client.status(verbose=True):
            path = os.path.relpath(l.path, start=self._wc)
            if path == ".":
                continue
            
            current = tree
            for node in path.split(os.sep):
                if not current.hasChild(node):
                    new = SvnStatusItem(
                        l,
                        parent=current
                    )
                    current.addChild(node, new)
                current = current.getChild(node)


    def columnCount(self, parent: QModelIndex = None) -> int:
        return self._root_item.columnCount()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        if role not in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.DecorationRole, Qt.ItemDataRole.CheckStateRole]:
            return None

        item: SvnStatusItem = self.get_item(index)

        if index.column() in [SvnStatusItem.COLUMNS.index(c) for c in ["switched", "locked", "external"]]:
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if item.data(index.column()) else Qt.CheckState.Unchecked

        else:        
            if role == Qt.ItemDataRole.DisplayRole:
                return item.data(index.column())

            if role == Qt.ItemDataRole.ForegroundRole:
                status = item.data(item.COLUMNS.index('type_raw_name'))

                if status in self.STATUS_COLORS:
                    return self.STATUS_COLORS[status]

            if role == Qt.ItemDataRole.DecorationRole:
                if index.column() == SvnStatusItem.COLUMNS.index("filename"):
                    return self.ICON_PROVIDER.icon(QFileIconProvider.IconType.Folder) if item.isFolder() else self.ICON_PROVIDER.icon(QFileInfo(item.path()))


    def get_item(self, index: QModelIndex = QModelIndex()) -> SvnStatusItem:
        if index.isValid():
            item: SvnStatusItem = index.internalPointer()
            if item:
                return item

        return self._root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._root_item.data(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: SvnStatusItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        if child_item := parent_item.child(row):
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        if child_item := self.get_item(index):
            parent_item: SvnStatusItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self._root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.childNumber(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: SvnStatusItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.childCount()


    def filePath(self, index):
        item: SvnStatusItem = self.get_item(index)
        return item.path()