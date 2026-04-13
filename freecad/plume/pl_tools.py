import os

import FreeCAD

RESOURCESPATH = os.path.join(os.path.dirname(__file__), "resources")

ICONPATH = os.path.join(RESOURCESPATH, "icons")
UIPATH = os.path.join(RESOURCESPATH, "ui")
TRANSLATIONSPATH = os.path.join(RESOURCESPATH, "translations")


translate = FreeCAD.Qt.translate