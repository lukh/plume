
import os
from collections import defaultdict

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate


class SubversionUpdateCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "update.svg"),
            "MenuText": translate("Plume", "Update the Working Copy"),
            "Accel": "P, U",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Update the Workking Copy</b> \
                    <br><br> \
                    Will update (pull) the entire Working Copy \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        pass


class SubversionCommitFileCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "commit.svg"),
            "MenuText": translate("Plume", "Commit files"),
            "Accel": "P, C",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Commit files</b> \
                    <br><br> \
                    opens a Dialog to select files to be commited \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        pass


class SubversionLockCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "lock.svg"),
            "MenuText": translate("Plume", "Lock files"),
            "Accel": "P, L",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Lock files</b> \
                    <br><br> \
                    opens a Dialog to select files to be locked \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        pass

class SubversionUnlockCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "unlock.svg"),
            "MenuText": translate("Plume", "Unlock files"),
            "Accel": "P, Z",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Unlock files</b> \
                    <br><br> \
                    opens a Dialog to select files to be unlocked \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        pass


class SubversionBrowse:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "browse.svg"),
            "MenuText": translate("Plume", "Browse repository/inventree for files and revisions"),
            "Accel": "P, B",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Browse</b> \
                    <br><br> \
                    opens a Dialog to select files to be opened \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        pass


Gui.addCommand("Plume_Update", SubversionUpdateCommand())
Gui.addCommand("Plume_Commit", SubversionCommitFileCommand())
Gui.addCommand("Plume_Lock", SubversionLockCommand())
Gui.addCommand("Plume_Unlock", SubversionUnlockCommand())
Gui.addCommand("Plume_BrowseRepository", SubversionBrowse())
