import os
import shutil
import tempfile
import sys
import zipfile

def prepare_folder_for_export(start_path):
    """
    return a list of temp files, renamed for inventree export
    """
    temp_dir = tempfile.mkdtemp()
    for root, dirs, files in os.walk(start_path):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            file_name = os.path.relpath(abs_path, start=start_path).replace(os.sep, "__")

            shutil.copy(abs_path, os.path.join(temp_dir, file_name))

    l = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            l.append(abs_path)
        
    return l



opt, par = getopt.getopt(sys.argv[1:], "-s:")
input_file = par[0]
output_file = par[1]
default_icon = "@CMAKE_INSTALL_DATAROOTDIR@/icons/hicolor/48x48/apps/org.freecad.FreeCAD.png"

def create_thumbnail(input_file, output_dir):
    # Read compressed file
    zfile = zipfile.ZipFile(input_file)
    files = zfile.namelist()

    # Check whether we have a FreeCAD document
    if "Document.xml" not in files:
        print(input_file, " doesn't look like a FreeCAD file")
        return None

    # Read thumbnail from file or use default icon
    image = "thumbnails/Thumbnail.png"
    if image in files:
        image = zfile.read(image)

        # Write icon to output_file
        thumb = open(os.path.join(output_dir, "Thumbnail.png"), "wb")
        thumb.write(image)
        thumb.close()