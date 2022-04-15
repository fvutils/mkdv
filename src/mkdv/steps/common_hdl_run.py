'''
Created on Apr 14, 2022

@author: mballance
'''
from mkdv.tools.hdl.hdl_tool_config import HdlToolConfig
from mkdv.tools.hdl.hdl_tool_mgr import HdlToolMgr
import os

from pypyr.context import Context


def run_step(context : Context):

    if "MKDV_TOOL" in os.environ.keys():
        tool = os.environ["MKDV_TOOL"]
    elif "MKDV_TOOL" in context.keys():
        tool = context["MKDV_TOOL"]
    else:
        raise Exception("MKDV_TOOL not specified")
  
    hdl_tool_mgr = HdlToolMgr.inst()
    cfg = HdlToolConfig(tool,
                        os.path.abspath(context["MKDV_CACHEDIR"]),
                        os.path.abspath(context["MKDV_RUNDIR"]))
    
    for key in [
        'MKDV_VL_DEFINES', 
        'MKDV_VL_INCDIRS',
        'MKDV_VL_SRCS',
        'MKDV_VPI_LIBS',
        'MKDV_DPI_LIBS',
        'MKDV_TOP_MODULE',
        'MKDV_RUN_ARGS']:
        if key in context.keys():
            val = context[key]
            print("key=%s val=%s" % (key, str(val)))
            if isinstance(val, list):
                for p in val:
                    cfg.append(key, p)
            elif isinstance(val, str):
                for p in val.split():
                    cfg.append(key, p)
            else:
                print("TODO: is unknown")
                pass
    
    hdl_tool_mgr.run(cfg)    