'''
Created on Nov 16, 2021

@author: mballance
'''

class ToolConfig(object):
    
    VL_DEFINES = "VL_DEFINES"
    VL_INCDIRS = "VL_INCDIRS"
    VPI_LIBS = "VPI_LIBS"
    DPI_LIBS = "DPI_LIBS"
    DEBUG = "DEBUG"
    VALGRIND = "VALGRIND"
    
    def __init__(self):
        self.vars = {}

    def set(self, var, val):
        pass
    
    def append(self, var, val):
        pass
    
    def prepend(self, var, val):
        pass
    
    def var_l(self, var):
        ret = []
        if var in self.vars.keys():
            ret.extend(self.vars.keys())
        return ret
    
    def var_b(self, var, dflt=False):
        ret = dflt
        if var in self.vars.keys():
            ret = bool(self.vars[var])
        return ret
            
        
    