from enum import IntEnum
from collections import defaultdict

import sys
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QDir, Qt, QModelIndex
from PySide6.QtGui import QColor

from freecad.plume.svn.local import _STATUS_ENTRY
from freecad.plume.utils import plume_svn


class SVNFileSystemModel(QFileSystemModel):
    REVISION_COLUMN = 0
    STATUS_COLUMN = 1
    LAST_COMMIT_COLUMN = 2
    LAST_AUTHOR_COLUMN = 3
    SWITCHED_COLUMN = 4
    LOCKED_COLUMN = 5
    EXTERNAL_COLUMN = 6

    EXTRA_COLUMNS_COUNT = 7

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


        if index.column() < source_cols:
            if (
                role == Qt.ItemDataRole.ForegroundRole
            ):

                status = entry.type_raw_name.lower()

                if status in self.STATUS_COLORS:
                    return self.STATUS_COLORS[status]

            return super().data(index, role)


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
