import os

from setuptools import setup

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "freecad", "plume", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(
    name="plume",
    version=str(__version__),
    packages=["freecad", "freecad.plume"],
    maintainer="Vivien HENRY",
    maintainer_email="vivien.henry@inductivebrain.fr",
    url="https://github.com/lukh/plume",
    description="Plume is intend to help FreeCAD users to manage their libraries and projects, with the help of SVN and Inventree",
    include_package_data=True,
)
