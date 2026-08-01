'''
'Simple Tree Model Example' converted from C++/Qt 5 to Python 3/PyQt5.
Original example copyrighted from the Qt Company: http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
License is BSD as the original example.
'''

import os
from collections.abc import MutableMapping
from collections import OrderedDict, defaultdict, namedtuple

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

from freecad.plume.utils.plume_inventree import PlumeInventree


class InventreeModelItem:
    ICON_PROVIDER = QFileIconProvider()


    PART_COLS = ["name", "revision", "active", "component", "assembly"]
    COLUMNS = ['category'] + PART_COLS

    COLUMNS_COUNT = len(COLUMNS)

    def __init__(self, category, ipn, part, parent=None):
        # self._item_data = [data[0]] + [getattr(data[1], pf, None) for pf in self.PART_COLS]
        self._item_data = {
            "category":category, 
            "ipn":ipn, 
            "part":[getattr(part, pf, None) for pf in self.PART_COLS] if not isinstance(part, list) else part}

        self._parent_item = parent
        
        self._child_items = OrderedDict()

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
        return list(self._parent_item._child_items.values()).index(self)

    def columnCount(self):
        return self.COLUMNS_COUNT

    def data(self, column, role: int = None):
        if role == Qt.ItemDataRole.DisplayRole:
            if not self._item_data:
                return None
            if column < 0 or column >= self.columnCount():
                return None

            if self._item_data['category'] is not None and column == 0:
                return self._item_data['category']

            elif self._item_data['ipn'] is not None and column == 0:
                return self._item_data['ipn']

            elif column > 0:
                return self._item_data['part'][column-1]

            return None

        elif role == Qt.ItemDataRole.DecorationRole:
            if column == 0 and self._item_data['category'] is not None:
                return self.ICON_PROVIDER.icon(QFileIconProvider.IconType.Folder)

        elif role == Qt.ItemDataRole.CheckStateRole:
            if self._item_data['category'] is None and self._item_data['ipn'] is None:
                if column in [InventreeModelItem.COLUMNS.index(c) for c in ["active", "component", "assembly"]]:
                    return Qt.CheckState.Checked if self._item_data['part'][column-1] else Qt.CheckState.Unchecked



    def parent(self):
        return self._parent_item
        
    def __repr__(self) -> str:
        result = f"<treeitem.InventreeModelItem at 0x{id(self):x}"
        for d in self._item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self._child_items)} children>"
        return result

class InventreeModel(QAbstractItemModel):
    def __init__(self, parent=None) :
        super().__init__(parent)

        self._root_item = InventreeModelItem(category=None, ipn=None, part=[None for k in InventreeModelItem.PART_COLS])



    def _repr_recursion(self, item: InventreeModelItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        print(item)
        for child in item._child_items.values():
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self._root_item)


    def load(self, url, **kwargs):
        self._inventree = PlumeInventree(url, **kwargs)

        self._root_item = InventreeModelItem(category=None, ipn=None, part=[None for k in InventreeModelItem.PART_COLS])

        self._setupModelData()

    def _setupModelData(self):
        tree = self._root_item

        for c in self._inventree.get_categories():
            path = c.pathstring
            current = tree
            for node in path.split(os.sep):
                if not current.hasChild(node):
                    new = InventreeModelItem(
                        category=c.name, ipn=None, part=None,
                        parent=current
                    )
                    current.addChild(node, new)
                current = current.getChild(node)


                parts_by_ipn = defaultdict(list)
                for p in self._inventree.get_parts(category=c.pk):
                    parts_by_ipn[p.IPN].append(p)

                for ipn in parts_by_ipn:
                    new_part = InventreeModelItem(
                        category=None, ipn=ipn, part=None,
                        parent=current
                    )
                    current.addChild(ipn, new_part)

                    for p in parts_by_ipn[ipn]:
                        new_part_version = InventreeModelItem(
                            category=None, ipn=None, part=p,
                            parent = new_part
                        )
                        new_part.addChild(p.revision, new_part_version)



    def columnCount(self, parent: QModelIndex = None) -> int:
        return self._root_item.columnCount()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        if role not in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DecorationRole, Qt.ItemDataRole.CheckStateRole]:
            return None

        item: InventreeModelItem = self.get_item(index)

        return item.data(index.column(), role=role)


    def get_item(self, index: QModelIndex = QModelIndex()) -> InventreeModelItem:
        if index.isValid():
            item: InventreeModelItem = index.internalPointer()
            if item:
                return item

        return self._root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return (["Category/Part"] + InventreeModelItem.PART_COLS)[section]

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: InventreeModelItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        if child_item := parent_item.child(row):
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        if child_item := self.get_item(index):
            parent_item: InventreeModelItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self._root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.childNumber(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: InventreeModelItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.childCount()


