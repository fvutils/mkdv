'''
Created on Apr 14, 2022

@author: mballance
'''

import os
from mkdv import get_packages_dir
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv

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
        cfg = Config(file=cfg_file)
        
        self.cm = CoreManager(cfg)
        
        packages_dir = get_packages_dir()
        project_dir = os.path.dirname(packages_dir)
        self.cm.add_library(Library("project", project_dir))
        
    def get_depends(self, vlnv):
        top_flags = { "is_toplevel": True}
        
        core_deps = self.cm.get_depends(Vlnv(vlnv), flags=top_flags)
        
        return core_deps
        
    def collect_files(self, core_deps, file_types, flags, is_include):
        
        files = []

        file_flags = { "is_toplevel": True}
        file_flags.update(flags)
        
        for dep in core_deps:
            
            for f in dep.get_files(file_flags):
                if file_types is None or f['file_type'] in file_types:
                    t_is_include = 'include_path' in f.keys() and f['include_path']

                    if t_is_include == is_include:
                        files.append(os.path.join(dep.core_root, f['name']))
                    

        return files
        
        
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = CoreDbMgr()
        return cls._inst
    