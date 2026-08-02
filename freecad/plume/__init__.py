import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "pysvn"))

import svn

import pip_system_certs.bootstrap
pip_system_certs.bootstrap.bootstrap()

