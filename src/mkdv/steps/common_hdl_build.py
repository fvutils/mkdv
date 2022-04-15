'''
Created on Apr 14, 2022

@author: mballance
'''
from pypyr.context import Context
from pkgutil import iter_modules, walk_packages
from mkdv.plugin_mgr import PluginMgr
from mkdv.tools.hdl.hdl_tool_mgr import HdlToolMgr
from mkdv.tools.hdl.hdl_tool_config import HdlToolConfig
import os

def run_step(context : Context):
    print("common_hdl_build")
    
    if "MKDV_TOOL" in os.environ.keys():
        tool = os.environ["MKDV_TOOL"]
    elif "MKDV_TOOL" in context.keys():
        tool = context["MKDV_TOOL"]
    else:
        raise Exception("MKDV_TOOL not specified")
  
    hdl_tool_mgr = HdlToolMgr.inst()
    cfg = HdlToolConfig(tool,
                        context["MKDV_CACHEDIR"],
                        context["MKDV_RUNDIR"])
    
    for key in [
        'MKDV_VL_DEFINES', 
        'MKDV_VL_INCDIRS',
        'MKDV_VL_SRCS',
        'MKDV_VPI_LIBS',
        'MKDV_DPI_LIBS']:
        if key in context.keys():
            val = context[key]
            print("key=%s val=%s" % (key, str(val)))
            if isinstance(val, list):
                for p in val:
                    cfg.append(key, p)
            elif isinstance(val, str):
                print("TODO: is a string")
                pass
            else:
                print("TODO: is unknown")
                pass
    
    hdl_tool_mgr.setup(cfg)
    
#    for l,n,p in walk_packages():
#        print("name=%s ispkg=%s" % (n, p))
        
#    for finder, name, ispkg in iter_modules():
#        print("name=%s ispkg=%s" % (name, ispkg))
        