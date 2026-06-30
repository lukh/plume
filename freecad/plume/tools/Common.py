import os
from collections import defaultdict

from PySide.QtWidgets import QMessageBox

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.widgets import ManageSubversionWorkingCopiesDialog

from freecad.plume.svn.exception import SvnException
from freecad.plume.utils.plume_svn import PlumeSvn, PlumeSvnException
from freecad.plume.utils.selector import PlumeSelection
from freecad.plume.utils.fc_utils import read_repo_config, write_repo_config

def catch_svn(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (PlumeSvnException, SvnException) as e:
                App.Console.PrintMessage(f"SVN ERROR : {str(e)}")
                QMessageBox.critical(None, "SVN ERROR", str(e))

        return wrapper


class CommonCommand:
    def log(self, msg):
        App.Console.PrintMessage(f'Plume : {msg}\n')

    def get_files_from_objects(self):
        sel = Gui.Selection.getSelection()
        paths = [obj.Document.FileName for obj in sel]

        paths += [p for p in PlumeSelection.instance().getSelection() if os.path.isfile(p)]

        return list(set(paths))

    def get_related_objects(self, object):
        """
        return all related object (root included)
        """
        def traverse(root):
            if hasattr(root, "PlumeIPN"):
                yield root
            if hasattr(root, "Group"):
                for obj in root.Group:
                    if hasattr(obj, "LinkedObject"):
                        obj = obj.LinkedObject
                    yield from traverse(obj)

        return list(traverse(object))

    def get_related_paths(self, object):
        """
        return all (absolute) paths related to an object
        """
        objects = list(self.get_related_objects(object))

        return list(set([o.Document.FileName for o in objects]))

    def svn(self):
        pl_snv = None
        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wc_path = param.GetString("CurrentWorkingCopy")
            if wc_path:
                pl_snv = PlumeSvn(wc_path)
            else:
                App.Console.PrintMessage(translate("plume", f"Can't load working copy\n"))

        return pl_snv

    def config(self):
        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wc_path = param.GetString("CurrentWorkingCopy")
            data = read_repo_config(wc_path)
        else:
            raise ValueError('Repo Config : file .plume.json not found')

        return data

    def get_export_dir(self, abs_root_path):
        svn = self.svn()
        repo_config = self.config()

        dest = None
        if config['export_in_svn']:
            if config['svn_export_mode'] == "subfolder":
                dest = os.path.join(abs_root_path, repo_config["svn_export_subfolder"])
            else:
                dest = os.path.join(svn.working_copy, repo_config["svn_export_rootfolder"], os.path.relpath(abs_root_path, start=svn.working_copy))

        if config['export_in_inventree'] and dest is None:
            dest = os.path.join(abs_root_path, "inventree-exports") # TODO : define an external folder (from WC) ? uncommited ?

        return dest


