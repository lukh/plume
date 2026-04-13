import os

import FreeCAD as App
import FreeCADGui as Gui

from freecad.plume.pl_tools import TRANSLATIONSPATH, translate

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()


class Plume(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    MenuText = "Plume"
    ToolTip = "Plume is intend to help FreeCAD users to manage their libraries and projects, with the help of SVN and Inventree"
    Icon = """
        /* XPM */
        static char * feather_xpm[] = {
            "16 16 91 1",
            " 	c None",
            ".	c #915E34",
            "+	c #A46B36",
            "@	c #AE7237",
            "#	c #A26A35",
            "$	c #9A6434",
            "%	c #83553B",
            "&	c #9E673B",
            "*	c #A76D39",
            "=	c #A36B3A",
            "-	c #764C3E",
            ";	c #7E5238",
            ">	c #9C6636",
            ",	c #7F5340",
            "'	c #AB7038",
            ")	c #A86E38",
            "!	c #A66D39",
            "~	c #925F38",
            "{	c #67433A",
            "]	c #A46B39",
            "^	c #A56C37",
            "/	c #865838",
            "(	c #9B663B",
            "_	c #734B42",
            ":	c #89593E",
            "<	c #936035",
            "[	c #8D5C37",
            "}	c #7A4F38",
            "|	c #B1763B",
            "1	c #AA7037",
            "2	c #8C5B38",
            "3	c #6F4939",
            "4	c #6C483B",
            "5	c #B3793F",
            "6	c #AE7641",
            "7	c #AE7338",
            "8	c #9A6538",
            "9	c #7F5339",
            "0	c #805439",
            "a	c #956641",
            "b	c #A27149",
            "c	c #734B39",
            "d	c #A6764A",
            "e	c #AF7338",
            "f	c #AF7439",
            "g	c #B0753A",
            "h	c #B2783D",
            "i	c #B47B41",
            "j	c #AE7844",
            "k	c #8E6448",
            "l	c #75574D",
            "m	c #9F744E",
            "n	c #CB9C68",
            "o	c #B0763B",
            "p	c #B3783E",
            "q	c #B57C42",
            "r	c #B27B46",
            "s	c #6F4838",
            "t	c #7C6159",
            "u	c #B18B69",
            "v	c #D5AA79",
            "w	c #B57C43",
            "x	c #B9824A",
            "y	c #BD8851",
            "z	c #BB8A57",
            "A	c #BC8E5F",
            "B	c #C69B6D",
            "C	c #AF9683",
            "D	c #DFBB90",
            "E	c #FDE2BD",
            "F	c #BE8953",
            "G	c #C4925D",
            "H	c #CA9B68",
            "I	c #D2A675",
            "J	c #DAB283",
            "K	c #D5B693",
            "L	c #D4BFA7",
            "M	c #FDE5C2",
            "N	c #CB9C69",
            "O	c #D3A876",
            "P	c #DEB789",
            "Q	c #E8C79C",
            "R	c #F2D5AF",
            "S	c #CEC1B3",
            "T	c #F7E2C4",
            "U	c #FDE2BC",
            "V	c #FDEAD1",
            "W	c #EEDFCA",
            "X	c #CFC9C4",
            "Y	c #FDE4C2",
            "Z	c #CECECE",
            ".+@@@           ",
            "@#$%&@*         ",
            "@@=-;>,'@       ",
            " @)!@~{]^/      ",
            "  @@(_:<[}|     ",
            "  @@)@123456    ",
            "   @@7890abcd   ",
            "    efghijklmn  ",
            "     opqrcstuv  ",
            "      wxyzABCDE ",
            "       FGHIJKLM ",
            "        NOPQRST ",
            "          UMVWX ",
            "            MYZ ",
            "              ZZ",
            "                "};
    """

    toolbox_repository = [
        "Plume_Connect",
        "Plume_Update",
        "Plume_Lock",
        "Plume_Unlock",
        "Plume_BrowseRepository"
    ]

    toolbox_project = [
        "Plume_CreateNewProject",
        "Plume_CommitFile",
        "Plume_CommitProject",
        "Plume_CheckProject",
        "Plume_ReleaseProject",
    ]

    toolbox_libraries = [
        "Plume_CreateNewLibrary",
        "Plume_CommitLibrary",
        "Plume_CheckLibrary",
        "Plume_ReleaseLibrary",
    ]

    toolbox_object = [
        "Plume_InitializeObject"
        "Plume_UpdateLinkToRelease"
    ]


    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        pass
        # from freecad.plume import (
        #     utilities,
        # )
        # from freecad.plume.pl_tools import translate

        # self.appendToolbar(translate("frameforge", "Drawing Primitives"), self.toolbox_drawing)
        # self.appendMenu(translate("frameforge", "Drawing Primitives"), self.toolbox_drawing)

    def Activated(self):
        """
        code which should be computed when a user switch to this workbench
        """
        pass
        # from freecad.frameforge.ff_tools import translate

        # App.Console.PrintMessage(translate("frameforge", "Workbench frameforge activated.") + "\n")

    def Deactivated(self):
        """
        code which should be computed when this workbench is deactivated
        """
        pass
        # from freecad.frameforge.ff_tools import translate

        # App.Console.PrintMessage(translate("frameforge", "Workbench frameforge de-activated.") + "\n")


Gui.addWorkbench(Plume())
