import os
from collections import defaultdict
import uuid

from PySide.QtWidgets import QInputDialog, QMessageBox, QFileDialog

import FreeCAD as App
import FreeCADGui as Gui
import TechDrawGui
import TechDraw

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate
from freecad.plume.utils.widgets import open_or_create_directory
from freecad.plume.utils.fc_utils import create_thumbnail, get_inventree_credentials
from freecad.plume.utils.plume_inventree import PlumeInventree

from freecad.plume.tools.Common import CommonCommand, catch_svn

class InitializePlumeObjectCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "initialize-object.svg"),
            "MenuText": translate("Plume", "Initialize a Plume object"),
            "Accel": "P, I",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Initialize a Plume Object</b> \
                    <br><br> \
                    Select an Object in the tree and then launch the tool \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        sel = Gui.Selection.getSelection()
        if len(sel) == 0:
            return False

        for obj in sel:
            if hasattr(obj, "PlumeIPN"):
                return False

        return True

    def Activated(self):
        sel = Gui.Selection.getSelection()

        # TODO : get or find PlumeIPN

        for obj in sel:
            if not hasattr(obj, "PlumeIPN"):
                obj.addProperty(
                    "App::PropertyString",
                    "PlVersion",
                    "Plume",
                    "Version",
                ).PlVersion = ""
                obj.addProperty(
                    "App::PropertyString",
                    "PlRevision",
                    "Plume",
                    "Revision",
                ).PlRevision = ""

                obj.addProperty(
                    "App::PropertyEnumeration",
                    "PlType",
                    "Plume",
                    "Plume Type",
                ).PlType = ["MechanicalPart", "MechanicalAssembly"]

                obj.addProperty(
                    "App::PropertyEnumeration",
                    "PlSourcing",
                    "Plume",
                    "Sourcing of the Part Object",
                ).PlSourcing = ['Manufactured', 'Purchased']

                obj.addProperty(
                    "App::PropertyBool",
                    "PlVirtual",
                    "Plume",
                    "Virtual Object : Software, Licence, Process ...",
                ).PlVirtual = False

                # obj.addProperty(
                #     "App::PropertyBool",
                #     "PlManufactured",
                #     "Plume",
                #     "Manufactured Object",
                # ).PlManufactured = True


                # 0 -- Prop_None, No special property attribute
                # 1 -- Prop_ReadOnly, Property is read-only in the editor
                # 2 -- Prop_Transient, Property won't be saved to file
                # 4 -- Prop_Hidden, Property won't appear in the editor
                # 8 -- Prop_Output, Modified property doesn't touch its parent container
                # 16 -- Prop_NoRecompute, Modified property doesn't touch its container for recompute
                # 32 -- Prop_NoPersist, Property won't be saved to file at all
                # obj.addProperty("App::PropertyString", "MyCustomProperty", "", "", 8)
                obj.addProperty(
                    "App::PropertyString",
                    "SvnStatus",
                    "Plume",
                    "SVN Status of the related file",
                    1 + 2 + 8 + 16 + 32
                ).SvnStatus = ""

                obj.addProperty(
                    "App::PropertyString",
                    "SvnSwicthed",
                    "Plume",
                    "SVN Switch to another file",
                    1 + 2 + 8 + 16 + 32
                ).SvnSwicthed = ""

                obj.addProperty(
                    "App::PropertyStringList",
                    "ExportedSteps",
                    "Plume",
                    "ExportedSteps",
                ).ExportedSteps = []
                obj.setEditorMode("ExportedSteps", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyStringList",
                    "ExportedTechDrawPages",
                    "Plume",
                    "ExportedTechDrawPages",
                ).ExportedTechDrawPages = []
                obj.setEditorMode("ExportedTechDrawPages", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyStringList",
                    "ExportedCNCJobs",
                    "Plume",
                    "ExportedCNCJobs",
                ).ExportedCNCJobs = []
                obj.setEditorMode("ExportedCNCJobs", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyStringList",
                    "ExportedDXFs",
                    "Plume",
                    "ExportedDXFs",
                ).ExportedCNCJobs = []
                obj.setEditorMode("ExportedDXFs", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyString",
                    "PlumeIPN",
                    "Plume",
                    "Unique Identifier for Plume",
                ).PlumeIPN = str(uuid.uuid4())
                obj.setEditorMode("PlumeIPN", 1)  # user doesn't change !



class EditExportedObjectsCommand:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "initialize-object.svg"),
            "MenuText": translate("Plume", "Edit Exported Objects"),
            "Accel": "P, I",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Edit exported Plume Object</b> \
                    <br><br> \
                    Select the Plume Object in the tree, and related Group of objects or Objects and then launch the tool \
                    </p></body></html>",
            ),
        }

    def IsActive(self):
        sel = Gui.Selection.getSelection()
        if len(sel) > 0:
            if hasattr(sel[0], "PlumeIPN"):
                return True
    
        return False

    def Activated(self):
        sel = Gui.Selection.getSelection()
        root_obj = sel.pop(0)

        cat, ok = QInputDialog.getItem(None, "Add to", "Add objects to : ", ['ExportedSteps', 'ExportedTechDrawPages', 'ExportedDXFs', 'ExportedCNCJobs'])
        if ok:
            setattr(root_obj, cat, [o.Name for o in sel])


class BuildReleaseFilesCommand(CommonCommand): # Should be named Release, and rename Release to Tag... and allow a dry gen
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "initialize-object.svg"),
            "MenuText": translate("Plume", "Build release files"),
            "Accel": "P, I",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>Build release files for a given object</b> \
                    <br><br> \
                    Select the Plume Object in the tree, and fire \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        sel = Gui.Selection.getSelection() # here, the object is needed for future use
        if len(sel) != 1:
            return False

        obj = sel[0]
        if not hasattr(obj, "PlumeIPN"):
            return False

        if obj.PlVersion == "" or obj.PlRevision == "":
            return False

        root_path = obj.Document.FileName

        svn = self.svn()
        if svn is None:
            return False

        if not (\
            svn.is_in_repository(root_path) and \
            svn.is_release_path(root_path) and \
            svn.is_path_clean(root_path) and \
            (not svn.is_path_external(svn.get_rel_path(root_path))) and \
            (not svn.is_path_switched(svn.get_rel_path(root_path))) and \
            (not svn.is_path_locked(svn.get_rel_path(root_path)))
        ):
            return False

        return True

    def Activated(self):
        def recursive_scan(group, path=""):
            if path == "":
                path = group.Label

            if group.TypeId == 'App::DocumentObjectGroup':
                for obj in group.Group:
                    if obj.TypeId == 'App::DocumentObjectGroup':
                        yield from recursive_scan(obj, path=path + "/" + obj.Label)
                    
                    else:
                        print(" - ", path, obj.Label)
                        yield (path, obj)
            

        svn = self.svn()

        sel = Gui.Selection.getSelection()
        root_obj = sel[0]

        abs_root_path = os.path.split(root_obj.Document.FileName)[0]
        dest = self.get_export_dir(abs_root_path)
        if dest is None:
            self.log('no dest for export !')
            return
        
        # main shape
        os.makedirs(dest, exist_ok=True)
        root_obj.Shape.exportStep(os.path.join(dest, root_obj.Label + ".step"))

        # exported objects (plans, etc)
        categories = ['ExportedSteps', 'ExportedTechDrawPages', 'ExportedDXFs', 'ExportedCNCJobs']
        for exp_objects, cat in [(getattr(root_obj, c), c)for c in categories]:
            for eo_name in exp_objects:
                eo = root_obj.Document.getObject(eo_name)
                for (subpath, obj) in recursive_scan(eo):
                    file_dirpath = os.path.join(dest, subpath)
                    os.makedirs(file_dirpath, exist_ok=True)

                    file_path = os.path.join(file_dirpath, obj.Label)

                    match cat:
                        case 'ExportedSteps':
                            if hasattr(obj, "Shape"):
                                file_path += ".step"
                                obj.Shape.exportStep(file_path)
                                App.Console.PrintMessage(f'Exporting {file_path}\n')
                            else:
                                App.Console.PrintError(f"obj has no Shape: {obj.Label}\n")

                        case 'ExportedTechDrawPages':
                            if obj.TypeId == "TechDraw::DrawPage":
                                file_path += ".pdf"
                                TechDrawGui.exportPageAsPdf(obj, file_path)
                            else:
                                App.Console.PrintError(f"obj is not a TechDraw: {obj.Label}\n")

                        case 'ExportedDXFs':
                            if obj.TypeId == "TechDraw::DrawPage":
                                file_path += ".dxf"
                                TechDraw.writeDXFPage(obj, file_path)
                            else:
                                App.Console.PrintError(f"obj is not a TechDraw: {obj.Label}\n")

                        case 'ExportedCNCJobs':
                            pass # TODO...

        # TODO : BOM, CSV ?

        # Thumbnail 
        create_thumbnail(root_obj.Document.FileName, dest)




class ReleaseFilesCommand(CommonCommand):
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONPATH, "initialize-object.svg"),
            "MenuText": translate("Plume", "release export files"),
            "Accel": "P, I",
            "ToolTip": translate(
                "Plume",
                "<html><head/><body><p><b>release files for a given object</b> \
                    <br><br> \
                    Select the Plume Object in the tree, and fire \
                    </p></body></html>",
            ),
        }

    @catch_svn
    def IsActive(self):
        sel = Gui.Selection.getSelection() # here, the object is needed for future use
        if len(sel) != 1:
            return False

        obj = sel[0]
        if not hasattr(obj, "PlumeIPN"):
            return False

        if obj.PlVersion == "" or obj.PlRevision == "":
            return False

        root_path = obj.Document.FileName

        svn = self.svn()
        if svn is None:
            return False

        if not (\
            svn.is_in_repository(root_path) and \
            svn.is_release_path(root_path) and \
            # svn.is_path_clean(root_path) and \
            (not svn.is_path_external(svn.get_rel_path(root_path))) and \
            (not svn.is_path_switched(svn.get_rel_path(root_path))) and \
            (not svn.is_path_locked(svn.get_rel_path(root_path)))
        ):
            return False

        return True

    def Activated(self):
        svn = self.svn()
        repo_config = self.config()

        sel = Gui.Selection.getSelection()
        root_obj = sel[0]

        abs_root_path = os.path.split(root_obj.Document.FileName)[0]
        dest = self.get_export_dir(abs_root_path)
        if dest is None:
            self.log('no dest for export !')
            return

        # push to Inventree
        username, password, token = get_inventree_credentials(repo_config)
        pi = PlumeInventree(url, token=token, username=username, password=password, strict=False)

        categories = pi.get_category_paths()
        category_path, ok = QInputDialog.getItem(None, "Select Category", "Category to create the Part", categories)
        if not ok:
            return False

        # commit
        if repo_config['export_in_svn']:
            svn.add(dest)
            svn.commit(f"Add export for {root_obj.Document.FileName}", [dest])

        pi.create_part(
            root_obj.PlumeIPN,
            root_obj.Label,
            root_obj.Comment,
            f"{root_obj.PlVersion}.{root_obj.PlRevision}",
            component=True,
            assembly=root_obj.PlType == "MechanicalAssembly",
            purchaseable=root_obj.PlSourcing == "Purchased",
            salable=False,
            virtual=root_obj.PlVirtual,
            attachment_folder=dest,
            category_path=category_path
        )

Gui.addCommand("Plume_InitializeObject", InitializePlumeObjectCommand())
Gui.addCommand("Plume_EditExportedObjects", EditExportedObjectsCommand())
Gui.addCommand("Plume_BuildReleaseFiles", BuildReleaseFilesCommand())
