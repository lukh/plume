from enum import IntEnum

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QListView
from PyQt6.QtCore import QDir, Qt, QModelIndex
from PyQt6.QtGui import QColor, QFileSystemModel


# class SVNRoles(IntEnum):
#     RevisionRole = Qt.ItemDataRole.UserRole + 1
#     StatusRole = Qt.ItemDataRole.UserRole + 2


class SVNFileSystemModel(QFileSystemModel):

    REVISION_COLUMN = 0
    STATUS_COLUMN = 1
    LAST_AUTHOR_COLUMN = 2
    SWITCHED_COLUMN = 3
    LOCKED_COLUMN = 4
    EXTERNAL_COLUMN = 5

    EXTRA_COLUMNS_COUNT = 6

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

        self._svn = {}
        # {
        #   path: {
        #       "revision": "1542",
        #       "status": "modified"
        #   }
        # }

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def svnInfo(self, path):
        return self._svn.get(path, {})

    def svnRevision(self, path):
        return self._svn.get(path, {}).get("revision", "")

    def svnStatus(self, path):
        return self._svn.get(path, {}).get("status", "")

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

            if section == (source_cols + self.LAST_AUTHOR_COLUMN):
                return "Last Author"

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

        # --------------------------------------
        # Custom roles
        # --------------------------------------

        # if role == SVNRoles.RevisionRole:
        #     return self.svnRevision(path)

        # if role == SVNRoles.StatusRole:
        #     return self.svnStatus(path)

        # --------------------------------------
        # Native columns
        # --------------------------------------

        if index.column() < source_cols:

            # Coloration du nom
            if (
                role == Qt.ItemDataRole.ForegroundRole
                # and index.column() == 0
            ):

                status = self.svnStatus(path).lower()

                if status in self.STATUS_COLORS:
                    return self.STATUS_COLORS[status]

            return super().data(index, role)

        # --------------------------------------
        # SVN columns
        # --------------------------------------

        if role == Qt.ItemDataRole.DisplayRole:

            if index.column() == source_cols:
                return self.svnRevision(path)

            if index.column() == source_cols + 1:
                return self.svnStatus(path)

        if role == Qt.ItemDataRole.ForegroundRole:

            status = self.svnStatus(path).lower()

            if status in self.STATUS_COLORS:
                return self.STATUS_COLORS[status]

        return None

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    def setSVNInfo(
        self,
        path,
        revision=None,
        status=None
    ):

        info = self._svn.setdefault(path, {})

        if revision is not None:
            info["revision"] = revision

        if status is not None:
            info["status"] = status

        self.refreshPath(path)

    def clearSVNInfo(self, path):

        if path in self._svn:
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
                # SVNRoles.RevisionRole,
                # SVNRoles.StatusRole,
            ]
        )




ROOT_DIR = "/home/lukhe/temp/PlumeTest"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QFileSystemModel + QTreeView")
        self.resize(800, 600)

        # Création du modèle
        self.model = SVNFileSystemModel()
        root_index = self.model.setRootPath(ROOT_DIR)

        self.model.setSVNInfo("/home/lukhe/temp/PlumeTest/projects/Velotoubo/trunk/Guidon.FCStd", revision="58", status="modified")

        # Création de la vue
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        # Dossier affiché au démarrage
        self.tree.setRootIndex(root_index)

        # Ajustement des colonnes
        # for col in range(4):
        #     self.tree.resizeColumnToContents(col)

        self.setCentralWidget(self.tree)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())