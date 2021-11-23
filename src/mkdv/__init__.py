from .mkdv_py import setup
import os
#from .tool_config import *
#from .job_spec import *

def get_packages_dir():
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    
    packages_dir = mkdv_dir

    while packages_dir != "":
        if os.path.basename(packages_dir) == "packages":
            break
        else:
            packages_dir = os.path.dirname(packages_dir)
            
    return packages_dir

