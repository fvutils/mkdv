'''
Created on Nov 19, 2021

@author: mballance
'''
import fusesoc
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv
from mkdv import get_packages_dir
import os
import logging
import yaml
import sys


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
    cfg = Config()
    
#    logging.basicConfig(level=logging.DEBUG)
    
    cm = CoreManager(cfg)

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
    cm.add_library(Library("project", project_dir), ignore_dirs)

    if args.library_path is not None:
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
        
    # Use detailed arguments
    core_deps = cm.get_depends(Vlnv(args.vlnv), flags=top_flags)

    flags = {}

    if hasattr(args, "flags") and args.flags is not None:
        for f in args.flags:
            subflags = f.split(',')
            for sf in subflags:
                flags[sf] = True
            
    file_type = None
    
    if args.file_type is not None:
        file_type = set()
        
        for t in args.file_type:
            subtypes = t.split(',')
            for st in subtypes:
                file_type.add(st)
                
    _extract_files(sys.stdout, core_deps, file_type, flags, args.include)
        
def _extract_files(out, core_deps, file_type, flags, include):
    files = []
    file_s = set()

    for d in core_deps:
        file_flags = {"is_toplevel": True}
        
#        if hasattr(args, "target") and args.target is not None:
#            file_flags["target"] = args.target
            
        # Bring in flags to specify which content is included
        file_flags.update(flags)
        
        d_files = d.get_files(file_flags)

        for f in d_files:
            if file_type is None or f['file_type'] in file_type:
                if include:
                    if 'include_path' in f.keys():
                        incdir = os.path.join(d.core_root, f['include_path'])
                    else:
                        incdir = os.path.join(d.core_root, os.path.dirname(f['name']))
                    if not incdir in file_s:
                        file_s.add(incdir)
                        files.append(incdir)
                elif 'is_include_file' not in f.keys() or not f['is_include_file']:
                    if os.path.join(d.core_root, f['name']) not in file_s:
                        file_s.add(os.path.join(d.core_root, f['name']))
                        files.append(os.path.join(d.core_root, f['name']))
    
    out.write(" ".join(files))
    out.write("\n")

