'''
Created on Aug 30, 2021

@author: mballance
'''
import asyncio
from mkdv.backends.backend import Backend
from mkdv.job_spec import JobSpec


class BackendLsf(Backend):
    
    def __init__(self):
        pass
    
    def quota(self):
        """Returns the max parallel jobs to launch"""
        return -1
    
    async def launch(self, js : JobSpec, cmdline, cwd=None):
        """Launches a new job and returns a proxy process"""
        lsf_cmdline = ['bsub', '-K', '-o', '/dev/null']
#        Lsf_cmdline.extend(['-J', js.fullname])
        lsf_cmdline.extend(cmdline)
        
        proc = await asyncio.subprocess.create_subprocess_exec( 
            *lsf_cmdline, cwd=cwd)
        
        return proc
