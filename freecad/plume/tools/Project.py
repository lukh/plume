import os
from collections import defaultdict

from PySide.QtWidgets import QInputDialog, QMessageBox, QFileDialog

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.widgets import ManageSubversionWorkingCopiesDialog, CommitDialog, open_or_create_directory

from freecad.plume.tools.Common import CommonCommand, catch_svn

from freecad.plume.utils.plume_svn import PlumeSvn, PlumeSvnException
from freecad.plume.utils.fc_utils import traverse

class CreateProjectCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "new-project.svg"),
            "MenuText": translate("Plume", "Create a new project"),
            "Accel": "P, P",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Create a new project directory and populate with needed subdir</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        return True


    @catch_svn
    def Activated(self):
        svn = self.svn()

        abs_root_path = QFileDialog.getExistingDirectory(None, "Select destination folder of the project", "")
        if not abs_root_path:
            return

        project_name, ok = QInputDialog.getText(None, "Project Folder Name", "Project Name/Folder")
        if not ok:
            return

        abs_path = os.path.join(abs_root_path, project_name)

        if not svn.is_in_repository(abs_root_path):
            QMessageBox.error(None, "Path Error", "Project not in repository")

        if os.path.exists(abs_path):
            QMessageBox.error(None, "Project already exists !", abs_path)
            return

        rel_path = svn.get_rel_path(abs_path)

        if QMessageBox.question(None, "About to create a new project", f"Do you want to create/commit folder under {rel_path} ({abs_path})?") != QMessageBox.StandardButton.Yes:
            return

        svn.create_project(rel_path)

        QMessageBox.information(None, "Project created", f"Project {rel_path} created !")


class SwitchCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "release-library.svg"),
            "MenuText": translate("Plume", "Switch a file"),
            "Accel": "P, P",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Switch a file to a released version</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            root_path = sel_paths[0]
            if not (\
                svn.is_in_repository(root_path) and \
                svn.is_trunk_path(root_path) and \
                svn.is_path_clean(root_path) and \
                (not svn.is_path_switched(svn.get_rel_path(root_path))) and \
                (not svn.is_path_external(svn.get_rel_path(root_path))) and \
                (not svn.is_path_locked(svn.get_rel_path(root_path)))
            ):
                return False

        elif len(sel_paths) == 0:
            # TODO open treewidget with filemodel
            return False

        return True

    @catch_svn
    def Activated(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            abs_path = sel_paths[0]
            rel_path = svn.get_rel_path(abs_path)

            _, _, filename = svn.split_trunk_path(rel_path)
            releases = svn.get_releases_available(rel_path)

            release, ok = QInputDialog.getItem(None, "Choose a release", f"release for file {rel_path}", releases)
            if ok:
                version, revision = release.split(".")

                release_name = os.path.splitext(filename)[0]

                svn.switch(rel_path, release_name, version, revision)

                App.closeDocument(os.path.splitext(filename)[0])
                App.openDocument(abs_path)


class UnswitchCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "check-project.svg"),
            "MenuText": translate("Plume", "Unswitch a file"),
            "Accel": "P, U",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Unswitch a file</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            root_path = sel_paths[0]
            if not (\
                svn.is_in_repository(root_path) and \
                svn.is_trunk_path(root_path) and \
                svn.is_path_clean(root_path) and \
                svn.is_path_switched(svn.get_rel_path(root_path)) and \
                (not svn.is_path_external(svn.get_rel_path(root_path))) and \
                (not svn.is_path_locked(svn.get_rel_path(root_path)))
            ):
                return False

        elif len(sel) == 0:
            # TODO open treewidget with filemodel
            return False

        return True

    @catch_svn
    def Activated(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            abs_path = sel_paths[0]
            rel_path = svn.get_rel_path(abs_path)

            svn.unswitch(rel_path)

            App.closeDocument(os.path.splitext(os.path.split(abs_path)[1])[0])
            App.openDocument(abs_path)



class ImportExternalCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "extern-add.svg"),
            "MenuText": translate("Plume", "Import external file to project"),
            "Accel": "P, P",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Import a (released) file as subversion's external into the project</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            root_path = sel_paths[0]
            if svn.is_in_repository(root_path) and svn.is_trunk_path(root_path):
                return True

        return False


    @catch_svn
    def Activated(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        doc_path = sel_paths[0]

        rel_root_path, _, _ = svn.split_trunk_path(svn.get_rel_path(doc_path))
        abs_root_path = svn.get_abs_path(rel_root_path)


        filenames, _ = QFileDialog.getOpenFileNames(None, caption="Select files to import", dir=svn.working_copy)

        if len(filenames) == 0:
            return
        if any([not svn.is_in_repository(f) for f in filenames]):
            return
        if any([not svn.is_release_path(f) for f in filenames]):
            return


        dest = open_or_create_directory(os.path.join(abs_root_path, "trunk"), "Select destination (sub) dir")
        if dest is None:
            return

        abs_root_path_trunk = os.path.join(abs_root_path, "trunk")

        if os.path.commonpath((dest, abs_root_path_trunk)) != abs_root_path_trunk:
            raise PlumeSvnException(f'{dest} : not in project root path {abs_root_path_trunk}!')

        dest_sub_dir = os.path.relpath(dest, os.path.join(abs_root_path, "trunk"))


        rel_target_paths = [svn.get_rel_path(f) for f in filenames]
        svn.add_externals(rel_root_path, dest_sub_dir, rel_target_paths)


class RemoveExternalCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "extern-remove.svg"),
            "MenuText": translate("Plume", "Remove external file from project"),
            "Accel": "P, R",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Remove an external file from the project</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        if len(sel_paths) == 1:
            root_path = sel_paths[0]
            if (\
                svn.is_in_repository(root_path) and \
                svn.is_trunk_path(root_path) and \
                svn.is_path_clean(root_path) and \
                (not svn.is_path_switched(svn.get_rel_path(root_path))) and \
                (not svn.is_path_external(svn.get_rel_path(root_path)))
            ):
                return True

        return False


    @catch_svn
    def Activated(self):
        svn = self.svn()

        sel_paths = self.get_files_from_objects()
        root_path = sel_paths[0]

        rel_root_path, _, _ = svn.split_trunk_path(svn.get_rel_path(root_path))
        externals = svn.get_externals(rel_root_path)

        ext_to_remove, ok = QInputDialog.getItem(None, "Choose a file to remove from project", f"Project {rel_root_path}", [k for k in externals])

        if ok and ext_to_remove:
            del externals[ext_to_remove]
            svn.set_externals(rel_root_path, externals, commit_msg=f'remove {ext_to_remove} from {root_path}')




class ReleaseCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "release-project.svg"),
            "MenuText": translate("Plume", "Release a file"),
            "Accel": "P, M",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Release a file</b> \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        sel = Gui.Selection.getSelection() # here, the object is needed for future use
        if len(sel) != 1:
            return False

        obj = sel[0]
        if not hasattr(obj, "PlumeID"):
            return False

        if obj.PlVersion == "" or obj.PlRevision == "":
            return False

        root_path = obj.Document.FileName

        svn = self.svn()
        if svn is None:
            return False

        if not (\
            svn.is_in_repository(root_path) and \
            svn.is_trunk_path(root_path) and \
            svn.is_path_clean(root_path) and \
            (not svn.is_path_external(svn.get_rel_path(root_path))) and \
            (not svn.is_path_switched(svn.get_rel_path(root_path))) and \
            (not svn.is_path_locked(svn.get_rel_path(root_path)))
        ):
            return False

        return True


    @catch_svn
    def Activated(self):
        release_ok = True
        errors_msgs = []

        svn = self.svn()
        sel = Gui.Selection.getSelection()

        root = sel[0]
        abs_root_path = root.Document.FileName
        rel_root_path = svn.get_rel_path(abs_root_path)

        version = root.PlVersion
        revision = root.PlRevision

        all_objects = list(traverse(root))
        related_objects = [o for o in all_objects if o != root]

        rootpath, subpath, filename = svn.split_trunk_path(svn.get_rel_path(rel_root_path))
        release_name = os.path.splitext(filename)[0]


        related_paths = []
        for p in [o.Document.FileName for o in related_objects]:
            rel_p = svn.get_rel_path(p)
            if not svn.is_in_repository(p):
                errors_msgs.append(f"{p} not in repo")
                release_ok = False
                continue

            if os.path.commonpath((os.path.split(abs_root_path)[0], os.path.split(p)[0])) != os.path.split(abs_root_path)[0]:
                errors_msgs.append(f"{p} not in root object path")
                release_ok = False
                continue

            if not svn.is_path_clean(p):
                errors_msgs.append(f"{p} not clean")
                release_ok = False
                continue
 
            if not svn.is_path_external(rel_p):
                if not svn.is_path_switched(rel_p):
                    errors_msgs.append(f"{p} not switched")
                    release_ok = False
                    continue

                if not svn.is_release_path(svn.get_switched_path(rel_p)):
                    errors_msgs.append(f"{p} not switched to released path")
                    release_ok = False
                    continue
            else:
                pass

            rp_rootpath, rp_subpath, rp_filename = svn.split_trunk_path(rel_p)
            if rp_rootpath != rootpath:
                errors_msgs.append(f"{rp_rootpath} not in root object path")
                release_ok = False
                continue

            if (rp_rootpath, rp_subpath, rp_filename) not in related_paths:
                related_paths.append((rp_rootpath, rp_subpath, rp_filename))


        sub_paths = [(subpath, filename)]
        for rp in related_paths:
            sub_paths.append((subpath, os.path.join(rp[1], rp[2])))

        if release_ok:
            if QMessageBox.question(None, "Confirm release", f'Do you want to release these files ? ...\n{"\n".join([svn.get_trunk_path(rootpath, sp[0], sp[1]) for sp in sub_paths])}') == QMessageBox.StandardButton.Yes:
                svn.release(rootpath, release_name, version, revision, sub_paths=sub_paths)

                QMessageBox.information(None, "Release ok", f'releasing ...\n{"\n".join([svn.get_trunk_path(rootpath, sp[0], sp[1]) for sp in sub_paths])}')

        else:
            QMessageBox.warning(None, "Can't release", "\n".join(errors_msgs))








Gui.addCommand("Plume_CreateProject", CreateProjectCommand())
Gui.addCommand("Plume_Switch", SwitchCommand())
Gui.addCommand("Plume_Unswitch", UnswitchCommand())
Gui.addCommand("Plume_ImportExternal", ImportExternalCommand())
Gui.addCommand("Plume_RemoveExternal", RemoveExternalCommand())
Gui.addCommand("Plume_Release", ReleaseCommand())
