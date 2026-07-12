import os
import json
from collections import defaultdict

from PySide.QtWidgets import QMessageBox, QInputDialog

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.widgets import ManageSubversionWorkingCopiesDialog

from freecad.plume.svn.exception import SvnException
from freecad.plume.utils.plume_inventree import PlumeInventree
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

    def get_children_objects(self, object):
        l = []
        if hasattr(object, "Group"):
            for obj in object.Group:
                if hasattr(obj, "PlumeIPN"):
                    if hasattr(obj, "LinkedObject"):
                        if hasattr(obj, "PlumeID"):
                            ref_id = obj.PlumeID
                        elif hasattr(obj, "PID"):
                            ref_id = obj.PID # FrameForge Id
                        else:
                            ref_id = "?"
                        obj = obj.LinkedObject
                    l.append((ref_id, obj))

        return l

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



    def inventree(self):
        repo_config = self.config()
        url = repo_config['inventree_url']

        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if param.IsEmpty():
            param.SetString("InvenTree Credentials", "")

        raw_creds = param.GetString("InvenTree Credentials")
        if raw_creds != "":
            creds = json.loads(raw_creds)
        else:
            creds = {}

        if url not in creds:
            user, ok = QInputDialog.getText(None, "Inventree user", f"User for {url}")
            password, ok = QInputDialog.getText(None, "Inventree password", f"password for {url}")
            token, ok = QInputDialog.getText(None, "Inventree token", f"token for {url}")

            creds[url] = {"user": user if user != "" else None, "password": password if password != "" else None, "token": token if token != "" else None}

            param.SetString("InvenTree Credentials", json.dumps(creds))


        user = creds[url]['user']
        password = creds[url]['password']
        token = creds[url]['token']

        pi = PlumeInventree(repo_config['inventree_url'], token=token, username=user, password=password, strict=False)
        return pi

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
        if repo_config['export_in_svn']:
            if repo_config['svn_export_mode'] == "subfolder":
                dest = os.path.join(abs_root_path, repo_config["svn_export_subfolder"])
            else:
                dest = os.path.join(svn.working_copy, repo_config["svn_export_rootfolder"], os.path.relpath(abs_root_path, start=svn.working_copy))

        if repo_config['export_in_inventree'] and dest is None:
            dest = os.path.join(abs_root_path, "inventree-exports") # TODO : define an external folder (from WC) ? uncommited ?

        return dest


