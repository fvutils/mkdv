'''
Created on Nov 16, 2021

@author: mballance
'''
from mkdv.tools.tool_config import ToolConfig
import os

class Tool(object):
    
    def config(self, spec, cfg : ToolConfig):
        cfg.append(ToolConfig.VL_DEFINES, "HAVE_HDL_CLOCKGEN")
        cfg.append(ToolConfig.VL_DEFINES, "HAVE_HDL_VIRTUAL_INTERFACE")
        cfg.append(ToolConfig.VL_DEFINES, "HAVE_BIND")
        pass
    
    def setup(self, spec, cfg : ToolConfig):
        vlog_options = []

        for inc in cfg.var_l(ToolConfig.VL_INCDIRS):
            vlog_options.append("+incdir+%s" % inc)
            
        for d in cfg.var_l(ToolConfig.VL_DEFINES):
            vlog_options.append("+define+%s" % d)
        
        pass
    
    def run(self, spec, cfg : ToolConfig):
        vsim_options = []
        
        for vpi in cfg.var_l(ToolConfig.VPI_LIBS):
            vsim_options.extend("-pli", vpi)
        for dpi in cfg.var_l(ToolConfig.DPI_LIBS):
            vsim_options.extend("-sv_lib", os.path.basename(dpi))
            
        if cfg.var_b(ToolConfig.DEBUG):
            vsim_options.append("-qwavedb=+report=class+signal+memory")
            
        if cfg.var_b(ToolConfig.VALGRIND):
            vsim_options.extend("-valgrind", "--tool=memcheck")
            
        pass