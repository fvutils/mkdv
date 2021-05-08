'''
Created on Dec 30, 2020

@author: mballance
'''

class TestSpec(object):
    
    def __init__(self, mkdv_mk, fullname, localname):
        self.mkdv_mk = mkdv_mk
        self.fullname = fullname
        self.localname = localname
        self.rundir = None
        self.variables = {}
        
    def append_run_variables(self, cmdline):
        """Append job variables to command-line list"""
        for v in self.variables.keys():
            cmdline.append(v + "=" + str(self.variables[v]))

