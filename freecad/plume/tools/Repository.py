
import os
from collections import defaultdict

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.widgets import ManageSubversionWorkingCopiesDialog, CommitDialog

from freecad.plume.tools.Common import CommonCommand, catch_svn

from freecad.plume.utils.plume_svn import PlumeSvn, PlumeSvnException

class SubversionManageWorkingCopies:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "browse.svg"),
            "MenuText": translate("Plume", "Manage Subversion Working Copies"),
            "Accel": "P, M",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Manage Subversion Working Copies</b> \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        return True

    @catch_svn
    def Activated(self):
        diag = ManageSubversionWorkingCopiesDialog()
        diag.exec()



class SubversionUpdateCommand(CommonCommand):
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

    @catch_svn
    def IsActive(self):
        return self.svn() is not None

    @catch_svn
    def Activated(self):
        self.svn().update()


class SubversionCommitFileCommand(CommonCommand):
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

    @catch_svn
    def IsActive(self):
        paths = self.get_files_from_objects()

        svn = self.svn()
        if svn is None:
            return False

        for p in paths:
            if not svn.is_in_repository(p):
                return False

            if svn.is_path_clean(p) and not svn.is_path_unversioned(p):
                return False

            if svn.is_path_switched(svn.get_rel_path(p)):
                return False

        return True

    @catch_svn
    def Activated(self):
        svn = self.svn()
        paths = [(svn.path_status(path).type_raw_name, path) for path in self.get_files_from_objects()]
        if len(paths) == 0:
            paths = [(s.type_raw_name, s.name) for s in svn.status() if not s.switched]

        ok, paths_to_commit, message = CommitDialog.get_commit_infos(paths=paths)

        if ok:
            for path in paths_to_commit:
                if svn.is_path_unversioned(path):
                    svn.add(path)
            svn.commit(message, paths=paths_to_commit)
                


class SubversionLockCommand(CommonCommand):
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

    @catch_svn
    def IsActive(self):
        paths = self.get_files_from_objects()

        if len(paths) == 0:
            return False

        svn = self.svn()
        if svn is None:
            return False

        for p in paths:
            if not svn.is_in_repository(p):
                return False

            if not svn.is_path_clean(p):
                return False

            if svn.is_path_switched(svn.get_rel_path(p)):
                return False

            if svn.is_path_locked(svn.get_rel_path(p)):
                return False

        return True

    @catch_svn
    def Activated(self):
        svn = self.svn()
        paths = self.get_files_from_objects()

        svn.lock(paths)

class SubversionUnlockCommand(CommonCommand):
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

    @catch_svn
    def IsActive(self):
        paths = self.get_files_from_objects()

        if len(paths) == 0:
            return False

        svn = self.svn()
        if svn is None:
            return False

        for p in paths:
            if not svn.is_in_repository(p):
                return False

            if not svn.is_path_clean(p):
                return False

            if svn.is_path_switched(svn.get_rel_path(p)):
                return False

            if not svn.is_path_locked(svn.get_rel_path(p)):
                return False

        return True

    @catch_svn
    def Activated(self):
        svn = self.svn()
        paths = self.get_files_from_objects()

        svn.unlock(paths)




Gui.addCommand("Plume_ManageWorkingCopies", SubversionManageWorkingCopies())
Gui.addCommand("Plume_Update", SubversionUpdateCommand())
Gui.addCommand("Plume_Commit", SubversionCommitFileCommand())
Gui.addCommand("Plume_Lock", SubversionLockCommand())
Gui.addCommand("Plume_Unlock", SubversionUnlockCommand())
