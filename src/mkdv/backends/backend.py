'''
Created on Aug 30, 2021

@author: mballance
'''
from mkdv.job_spec import JobSpec

class Backend(object):
    
    def quota(self):
        """Returns the max parallel jobs to launch"""
        raise NotImplementedError("quota is not implemented for class %s" % str(type(self)))
    
    async def launch(self, js : JobSpec, cmdline, cwd=None, stderr=None, stdout=None):
        """Launches a new job and returns a proxy process"""
        raise NotImplementedError("launch is not implemented for class %s" % str(type(self)))
        
    
    
    
    