'''
Created on Dec 30, 2020

@author: mballance
'''
from typing import Tuple, List, Dict, Set
from mkdv.runners.runner_spec import RunnerSpec

class JobSpec(object):
    
    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname
        self.description = None
       
        # Directory containing the job specification
        self.basedir = None
        
        # Run directory is populated late
        self.rundir = None

        # Cache directory is populated once jobs are known        
        self.cachedir = None
        
        # Run variables are associated with the job
        self.variables = {}

        # Attachments, parameters, and labels are used by 
        # the runner to determine what data to save for reporting        
        self.attachments : List[Tuple[str, str]] = []
        self.parameters : Dict[str,str] = {}
        self.labels : Dict[str,str] = {}

        # Rerun specifies whether this job execution is a rerun
        # of a previous unsuccessful run
                
        self.rerun = False
        self.limit = None
        
        # Runner spec contains data about *how* to execute the job
        self.runner_spec : RunnerSpec = None
        
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

