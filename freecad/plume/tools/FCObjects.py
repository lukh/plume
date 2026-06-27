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
            if hasattr(obj, "PlumeID"):
                return False

        return True

    def Activated(self):
        sel = Gui.Selection.getSelection()

        for obj in sel:
            if not hasattr(obj, "PlumeID"):
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
                ).PlType = ["MechanicalPart", "MechanicalAssembly", "OtherItem"]

                obj.addProperty(
                    "App::PropertyBool",
                    "PlManufactured",
                    "Plume",
                    "Manufactured Object",
                ).PlManufactured = True


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
                    1 + 2 + 8 + 16
                ).SvnStatus = ""

                obj.addProperty(
                    "App::PropertyString",
                    "SvnSwicthed",
                    "Plume",
                    "SVN Switch to another file",
                    1 + 2 + 8 + 16
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
                    "InventreeID",
                    "Plume",
                    "Unique Identifier for Inventree",
                ).InventreeID = ""
                obj.setEditorMode("InventreeID", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyString",
                    "PlumeID",
                    "Plume",
                    "Unique Identifier for Plume",
                ).PlumeID = str(uuid.uuid4())
                obj.setEditorMode("PlumeID", 1)  # user doesn't change !



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
        if len(sel) > 1:
            if hasattr(sel[0], "PlumeID"):
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
        dest = os.path.join(abs_root_path, "exports")

        os.makedirs(dest, exist_ok=True)
        root_obj.Shape.exportStep(os.path.join(dest, root_obj.Label + ".step"))

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





Gui.addCommand("Plume_InitializeObject", InitializePlumeObjectCommand())
Gui.addCommand("Plume_EditExportedObjects", EditExportedObjectsCommand())
Gui.addCommand("Plume_BuildReleaseFiles", BuildReleaseFilesCommand())
