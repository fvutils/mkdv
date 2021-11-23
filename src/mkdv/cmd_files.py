'''
Created on Nov 19, 2021

@author: mballance
'''
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv
import os
import logging


class _ConfigFile(object):
    """Dummy configuration file required by FuseSoC"""
    
    def __init__(self, content, name=""):
        self.name = name
        self.lines = content.splitlines()
        
    def seek(self, where):
        pass
    
    def __iter__(self):
        return iter(self.lines)

def cmd_files(args):
    cfg_file = _ConfigFile("")
    cfg = Config(file=cfg_file)
    
#    logging.basicConfig(level=logging.DEBUG)
    
    cm = CoreManager(cfg)

    for lib in args.library_path:
        colon_i = lib.find(':')
        if colon_i > 1:
            path = lib[colon_i+1:]
            lib_name = lib[:colon_i]
        else:
            path = lib
            lib_name = "cmdline"
            
        cm.add_library(Library(lib_name, path))
        
    top_flags = { "is_toplevel": True }
    if hasattr(args, "target") and args.target is not None:
        top_flags["target"] = args.target
        
    core_deps = cm.get_depends(Vlnv(args.vlnv), flags=top_flags)
    
#    top_core = core_deps[-1]
#    print("Targets: %s" % str(top_core.targets))
    
    
#    print("core_deps: %s" % str(core_deps))

    files = []
    
    for d in core_deps:
        file_flags = {"is_toplevel": True}
        
        if hasattr(args, "target") and args.target is not None:
            file_flags["target"] = args.target
        d_files = d.get_files(file_flags)

        for f in d_files:
            if args.file_type is None or f['file_type'] in args.file_type:
                is_include = 'include_path' in f.keys() and f['include_path']
                
                if is_include == args.include:
                    files.append(os.path.join(d.core_root, f['name']))

    print(" ".join(files))   
    