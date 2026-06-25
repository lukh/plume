import FreeCAD as App
import FreeCADGui as Gui

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
