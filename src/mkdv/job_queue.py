'''
Created on Jan 2, 2021

@author: mballance
'''
from mkdv.job_spec import JobSpec

class JobQueue(object):
    
    def __init__(self, mkdv_mk=None):
        self.mkdv_mk = mkdv_mk
        self.build_run = False
        self.build_pass = False
        self.cachedir = None
        self.reportdir = None
        self.jobs = []
        
    def append(self, j : JobSpec):
        self.jobs.append(j)
        
    def set_cachedir(self, cachedir):
        self.cachedir = cachedir
        for j in self.jobs:
            j.cachedir = cachedir
            
    def set_reportdir(self, reportdir):
        self.cachedir = reportdir
        for j in self.jobs:
            j.reportdir = reportdir
        
    