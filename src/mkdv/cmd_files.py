'''
Created on Nov 19, 2021

@author: mballance
'''
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv
import os


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
        
    core_deps = cm.get_depends(Vlnv(args.vlnv), flags={
        "target": args.target
        })

    files = []
    
    for d in core_deps:
        d_files = d.get_files({
            "is_toplevel": True,
            "target": args.target
            })

        for f in d_files:
            if args.file_type is None or f['file_type'] in args.file_type:
                files.append(os.path.join(d.core_root, f['name']))

    print(" ".join(files))   
    