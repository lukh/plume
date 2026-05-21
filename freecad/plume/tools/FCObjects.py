import os
from collections import defaultdict
import uuid

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import UIPATH, ICONPATH, TRANSLATIONSPATH, translate


class InitializePlumeObject:
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
        return len(Gui.Selection.getSelection()) > 0

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

                obj.addProperty(
                    "App::PropertyString",
                    "SvnStatus",
                    "Plume",
                    "SVN Status of the related file",
                ).SvnStatus = ""
                obj.setEditorMode("SvnStatus", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyString",
                    "SvnSwicthed",
                    "Plume",
                    "SVN Switch to another file",
                ).SvnSwicthed = ""
                obj.setEditorMode("SvnSwicthed", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyLinkListChild",
                    "ExportedTechDrawPages",
                    "Plume",
                    "ExportedTechDrawPages",
                ).ExportedTechDrawPages = []
                obj.setEditorMode("ExportedTechDrawPages", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyLinkListChild",
                    "ExportedCNCJobs",
                    "Plume",
                    "ExportedCNCJobs",
                ).ExportedCNCJobs = []
                obj.setEditorMode("ExportedCNCJobs", 1)  # user doesn't change !

                obj.addProperty(
                    "App::PropertyLinkListChild",
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



class RefreshPlumeObject:
    pass


Gui.addCommand("Plume_InitializeObject", InitializePlumeObject())
