'''
Created on Apr 14, 2022

@author: mballance
'''

import sys
import traceback

from pypyr.context import Context
from pypyr.errors import KeyNotInContextError
from mkdv.coredb_mgr import CoreDbMgr


def run_step(context : Context):
    print("filespec: %s" % str(context))
    
    context.assert_key_has_value("vlnv", "filespec")
    context.assert_key_exists("out", "filespec")
    
    vlnv = context.get_formatted("vlnv")
    
    dbm = CoreDbMgr.inst()
    
    deps = dbm.get_depends(vlnv)
    
    for e in context["out"]:
        if "name" not in e.keys():
            raise KeyNotInContextError("Missing 'name'")
        if "type" not in e.keys():
            raise KeyNotInContextError("Missing 'type'")
        name = e["name"]

        file_types = set()        
        for t in e["type"]:
            file_types.add(t.strip())

        flags = {}
        if "flags" in e.keys():
            for f in e["flags"]:
                flags[f] = True
                
        is_include = False
        if "include" in e.keys():
            is_include = bool(e["include"])
                
        files = dbm.collect_files(deps, file_types, flags, is_include)
        
        if name in context.keys():
            if isinstance(context[name], list):
                context[name].extend(files)
            elif isinstance(context[name], str):
                context[name] += " ".join(files)
            else:
                raise Exception("Target for files is an unsupported type %s" % str(type(context[name])))
        else:
            context[name] = files
    