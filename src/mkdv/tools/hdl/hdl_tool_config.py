'''
Created on Nov 16, 2021

@author: mballance
'''

class HdlToolConfig(object):
    
    VL_DEFINES = "MKDV_VL_DEFINES"
    VL_INCDIRS = "MKDV_VL_INCDIRS"
    VL_SRCS = "MKDV_VL_SRCS"
    VPI_LIBS = "MKDV_VPI_LIBS"
    DPI_LIBS = "MKDV_DPI_LIBS"
    TOP_MODULE = "MKDV_TOP_MODULE"
    RUN_ARGS = "MKDV_RUN_ARGS"
    DEBUG = "DEBUG"
    VALGRIND = "VALGRIND"
    
    def __init__(self, tool, cachedir, rundir):
        self.vars = {}
        self.tool = tool
        self.cachedir = cachedir
        self.rundir = rundir

    def set(self, var, val):
        raise Exception("set not implemented")
        pass
    
    def append(self, var, val):
        if var not in self.vars.keys():
            self.vars[var] = []
        self.vars[var].append(val)
    
    def prepend(self, var, val):
        if var not in self.vars.keys():
            self.vars[var] = []
        self.vars[var].insert(0, val)
    
    def var_l(self, var):
        ret = []
        if var in self.vars.keys():
            ret.extend(self.vars[var])
        return ret
    
    def var_b(self, var, dflt=False):
        ret = dflt
        if var in self.vars.keys():
            ret = bool(self.vars[var])
        return ret
            
        
    