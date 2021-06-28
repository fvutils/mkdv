'''
Created on Dec 30, 2020

@author: mballance
'''
from typing import Tuple, List, Dict, Set

class JobSpec(object):
    
    def __init__(self, mkdv_mk, fullname, localname):
        self.mkdv_mk = mkdv_mk
        self.fullname = fullname
        self.localname = localname
        self.description = None
        self.rundir = None
        self.variables = {}
        self.attachments : List[Tuple[str, str]] = []
        self.parameters : Dict[str,str] = {}
        self.labels : Dict[str,str] = {}
        
    def append_run_variables(self, cmdline):
        """Append job variables to command-line list"""
        for v in self.variables.keys():
            cmdline.append(v + "=" + str(self.variables[v]))
            
    def add_parameter(self, key, val, append=False):
        if key in self.parameters.keys() and append:
            self.parameters[key] += val
        else:
            self.parameters[key] = val
            
    def add_label(self, key, val, append=False):
        if key in self.labels.keys() and append:
            self.labels[key] += val
        else:
            self.labels[key] = val

