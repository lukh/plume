from enum import IntEnum
from collections import defaultdict

import sys
from PySide6.QtWidgets import QApplication, QWidget, QTreeView, QListView, QVBoxLayout, QFileSystemModel
from PySide6.QtCore import QDir, Qt, QModelIndex
from PySide6.QtGui import QColor

from PySide6.QtCore import Qt

from freecad.plume.svn.local import _STATUS_ENTRY
from freecad.plume.utils import plume_svn



class SVNFileSystemModel(QFileSystemModel):
    REVISION_COLUMN = 0
    STATUS_COLUMN = 1
    LAST_COMMIT_COLUMN = 3
    LAST_AUTHOR_COLUMN = 4
    SWITCHED_COLUMN = 5
    LOCKED_COLUMN = 6
    EXTERNAL_COLUMN = 7

    EXTRA_COLUMNS_COUNT = 8

    STATUS_COLORS = {
        "modified": QColor("#0066cc"),
        "added": QColor("#009900"),
        "deleted": QColor("#cc0000"),
        "conflicted": QColor("#ff6600"),
        "missing": QColor("#990099"),
        "unversioned": QColor("#808080"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._svn = defaultdict(_STATUS_ENTRY)

    # ---------------------------------------------------------
    # Columns
    # ---------------------------------------------------------

    def columnCount(self, parent=QModelIndex()):
        return super().columnCount(parent) + self.EXTRA_COLUMNS_COUNT

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole
    ):
        source_cols = super().columnCount()

        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):

            if section < source_cols:
                return super().headerData(
                    section,
                    orientation,
                    role
                )

            if section == (source_cols + self.REVISION_COLUMN):
                return "Revision"

            if section == (source_cols + self.STATUS_COLUMN):
                return "Status"

            if section == (source_cols + self.LAST_COMMIT_COLUMN):
                return "Last Commited Revision"

            if section == (source_cols + self.LAST_AUTHOR_COLUMN):
                return "Last Commited Author"

            if section == (source_cols + self.SWITCHED_COLUMN):
                return "Switched"

            if section == (source_cols + self.LOCKED_COLUMN):
                return "Locked"

            if section == (source_cols + self.EXTERNAL_COLUMN):
                return "External"

        return super().headerData(
            section,
            orientation,
            role
        )

    # ---------------------------------------------------------
    # Data
    # ---------------------------------------------------------

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid():
            return None

        source_cols = super().columnCount()

        path_index = self.index(
            index.row(),
            0,
            index.parent()
        )

        path = self.filePath(path_index)
        entry = self._svn[path]

        # --------------------------------------
        # Native columns
        # --------------------------------------

        if index.column() < source_cols:
            # Coloration du nom
            if (
                role == Qt.ItemDataRole.ForegroundRole
                # and index.column() == 0
            ):

                status = entry.type_raw_name.lower()

                if status in self.STATUS_COLORS:
                    return self.STATUS_COLORS[status]

            return super().data(index, role)

        # --------------------------------------
        # SVN columns
        # --------------------------------------

        if role == Qt.ItemDataRole.DisplayRole:

            if index.column() == (source_cols + self.REVISION_COLUMN):
                return entry.revision

            if index.column() == (source_cols + self.STATUS_COLUMN):
                return entry.type_raw_name

            if index.column() == (source_cols + self.LAST_COMMIT_COLUMN):
                return entry.last_committed_revision

            if index.column() == (source_cols + self.LAST_AUTHOR_COLUMN):
                return entry.last_committed_author

            if index.column() == (source_cols + self.SWITCHED_COLUMN):
                return entry.switched

            if index.column() == (source_cols + self.LOCKED_COLUMN):
                return entry.locked

            if index.column() == (source_cols + self.EXTERNAL_COLUMN):
                return entry.external

        if role == Qt.ItemDataRole.ForegroundRole:

            status = entry.type_raw_name.lower()

            if status in self.STATUS_COLORS:
                return self.STATUS_COLORS[status]

        return None

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    def setSVNInfo(
        self,
        status_entry
    ):
        path = status_entry.name
        self._svn[path] = status_entry

        self.refreshPath(path)

    def clearSVNInfo(self, path=None):
        if path is None:
            self._svn = defaultdict(default_factory=_STATUS_ENTRY)

        elif path in self._svn:
            del self._svn[path]

        self.refreshPath(path)

    def refreshPath(self, path):

        idx = self.index(path)

        if not idx.isValid():
            return

        first = self.index(
            idx.row(),
            0,
            idx.parent()
        )

        last = self.index(
            idx.row(),
            self.columnCount() - 1,
            idx.parent()
        )

        self.dataChanged.emit(
            first,
            last,
            [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.ForegroundRole,
            ]
        )




# ps = plume_svn.PlumeSvn("/home/lukhe/temp/naboo_svn/Sandbox", "https://svn.naboo/Sandbox")
# ps = plume_svn.PlumeSvn("/home/lukhe/temp/naboo_svn/Sandbox2", "https://svn.naboo/Sandbox2")
# ps = plume_svn.PlumeSvn("/home/lukhe/projets/dev/plume-tatooine-wc/Sandbox", "https://svn.tatooine/Sandbox")


ROOT_DIR = "/home/lukhe/temp/PlumeTest"
ps = plume_svn.PlumeSvn("/home/lukhe/temp/PlumeTest", "https://svn.hedwidge.local/PlumeTest")



class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(800, 600)

        # Création du modèle
        self.model = SVNFileSystemModel()
        root_index = self.model.setRootPath(ROOT_DIR)

        for s in ps.status(".", verbose=True):
            self.model.setSVNInfo(s)

        # Création de la vue
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        # Dossier affiché au démarrage
        self.tree.setRootIndex(root_index)

        # Ajustement des colonnes
        # for col in range(4):
        #     self.tree.resizeColumnToContents(col)

        l = QVBoxLayout()
        l.addWidget(self.tree)

        self.setLayout(l)


# app = QApplication(sys.argv)

# window = MainWindow()
# window.show()

# sys.exit(app.exec())