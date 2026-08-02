"""
Minimal setup.py to handle .pth file installation in site-packages root.

This is required because pyproject.toml alone cannot install .pth files
to the site-packages root directory where they need to be for Python
to process them during startup.
"""

from setuptools import setup
from setuptools.command.build_py import build_py
import os
import shutil


class BuildWithPth(build_py):
    """Custom build command that includes .pth file in site-packages root"""
    
    def run(self):
        super().run()
        # Copy .pth file to build directory root so it gets installed to site-packages
        pth_file = "pip_system_certs.pth"
        if os.path.exists(pth_file):
            dest = os.path.join(self.build_lib, pth_file)
            shutil.copy2(pth_file, dest)


if __name__ == "__main__":
    setup(cmdclass={'build_py': BuildWithPth})