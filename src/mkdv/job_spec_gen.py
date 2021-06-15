'''
Created on May 28, 2021

@author: mballance
'''

class JobSpecGen(object):
    """Job-spec generator runs a command to generate job-specs"""
    
    
    def __init__(self,
                 root_id,
                 srcdir,
                 mkdv_mk,
                 cmd,
                 path):
        self.root_id = root_id
        self.srcdir = srcdir
        self.mkdv_mk = mkdv_mk
        self.cmd = cmd
        self.path = path
        pass
    
    