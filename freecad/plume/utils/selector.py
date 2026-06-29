import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.utils.plume_svn import PlumeSvn

class PlumeSelection:
    _instance = None

    def __init__(self):
        self.tree_selection = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def getSelection(self):
        return self.tree_selection

    def setTreeSelection(self, paths):
        self.tree_selection = paths
        Gui.Command.update()

    def resetTreeSelection(self):
        self.tree_selection = []
        Gui.Command.update()



class SelectionObserver:
    def addSelection(self, document, object, element, position):
        param = App.ParamGet("User parameter:BaseApp/Preferences/Plume")
        if not param.IsEmpty():
            wc_path = param.GetString("CurrentWorkingCopy")
            if wc_path:
                document = App.getDocument(document)
                object = document.getObject(object)
                if hasattr(object, "PlumeID"):
                    svn = PlumeSvn(wc_path)
                    status = svn.path_status(document.FileName)
                    object.SvnStatus = status.type_raw_name
                    object.SvnSwicthed = str(status.switched)

    def clearSelection(self,doc):
        pass

