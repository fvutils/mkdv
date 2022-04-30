'''
Created on Nov 23, 2021

@author: mballance
'''
import logging
import os

from fusesoc.config import Config
from fusesoc.core import Core
from fusesoc.coremanager import CoreManager


logger = logging.getLogger(__name__)

class _ConfigFile(object):
    """Dummy configuration file required by FuseSoC"""
    
    def __init__(self, content, name=""):
        self.name = name
        self.lines = content.splitlines()
        
    def seek(self, where):
        pass
    
    def __iter__(self):
        return iter(self.lines)
    
class CoreManagerW(CoreManager):
    
    def __init__(self, cfg):
        super().__init__(cfg)

    def find_cores(self, library):
        found_cores = []
        path = os.path.expanduser(library.location)
        exclude = {".git"}
        if os.path.isdir(path) == False:
            raise OSError(path + " is not a directory")
        logger.debug("Checking for cores in " + path)
        for root, dirs, files in os.walk(path, followlinks=True):
            if "FUSESOC_IGNORE" in files:
                del dirs[:]
                continue
            dirs[:] = [directory for directory in dirs if directory not in exclude]

            # Skip anything inside the fusesoc tests directory, since
            # some of these core files are invalid
            if root.rfind("fusesoc/tests") != -1:
                continue
            
            for f in files:
                if f.endswith(".core"):
                    core_file = os.path.join(root, f)
                    try:
                        core = Core(core_file, self.config.cache_root)
                        found_cores.append(core)
                    except SyntaxError as e:
                        w = "Parse error. Ignoring file " + core_file + ": " + e.msg
                        logger.warning(w)
                    except ImportError as e:
                        w = 'Failed to register "{}" due to unknown provider: {}'
                        logger.warning(w.format(core_file, str(e)))
        return found_cores
    
            