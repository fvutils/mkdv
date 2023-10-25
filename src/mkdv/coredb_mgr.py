'''
Created on Apr 14, 2022

@author: mballance
'''

import os
import fusesoc
from mkdv import get_packages_dir
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv
from mkdv.core_manager_w import CoreManagerW

class _ConfigFile(object):
    """Dummy configuration file required by FuseSoC"""
    
    def __init__(self, content, name=""):
        self.name = name
        self.lines = content.splitlines()
        
    def seek(self, where):
        pass
    
    def __iter__(self):
        return iter(self.lines)

class CoreDbMgr(object):
    
    _inst = None
    
    def __init__(self):
        cfg_file = _ConfigFile("")
        cfg = Config()
        
        self.cm = CoreManager(cfg)

        ignore_dirs = set()

        # If we are using the source version of FuseSoC, exclude it
        # from the search path
        fusesoc_dir = os.path.dirname(os.path.abspath(fusesoc.__file__))
        if os.path.basename(os.path.dirname(fusesoc_dir)) == "fusesoc":
            ignore_dirs.add(os.path.dirname(fusesoc_dir))
        
        packages_dir = get_packages_dir()

        if os.path.isdir(os.path.join(packages_dir, "zephyr")):
            ignore_dirs.add(os.path.join(packages_dir, "zephyr"))

        project_dir = os.path.dirname(packages_dir)
        self.cm.add_library(Library("project", project_dir), ignore_dirs)
        
    def get_depends(self, vlnv):
        top_flags = { "is_toplevel": True}
        
        core_deps = self.cm.get_depends(Vlnv(vlnv), flags=top_flags)
        
        return core_deps
        
    def collect_files(self, core_deps, file_types, flags, is_include):
        
        files = []
        file_s = set()

        file_flags = { "is_toplevel": True}
        file_flags.update(flags)
        
        for dep in core_deps:
            
            for f in dep.get_files(file_flags):
                if is_include:
                    if 'include_path' in f.keys():
                        incdir = os.path.join(dep.core_root, f['include_path'])
                    else:
                        incdir = os.path.join(dep.core_root, os.path.dirname(f['name']))
                    if not incdir in file_s:
                        file_s.add(incdir)
                        files.append(incdir)
                elif 'is_include_file' not in f.keys() or not f['is_include_file']:
                    if os.path.join(dep.core_root, f['name']) not in file_s:
                        file_s.add(os.path.join(dep.core_root, f['name']))
                        files.append(os.path.join(dep.core_root, f['name']))                    
                    

        return files
        
        
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = CoreDbMgr()
        return cls._inst
    