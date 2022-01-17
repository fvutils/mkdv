'''
Created on Aug 30, 2021

@author: mballance
'''
import asyncio
from mkdv.backends.backend import Backend


class BackendSlurm(Backend):
    
    def __init__(self):
        pass
    
    def quota(self):
        """Returns the max parallel jobs to launch"""
        return 40
    
    async def launch(self, cmdline, cwd=None):
        """Launches a new job and returns a proxy process"""
        slurm_cmdline = ['srun', '-E']
        slurm_cmdline.extend(cmdline)
        
        proc = await asyncio.subprocess.create_subprocess_exec( 
            *slurm_cmdline, cwd=cwd)
        
        return proc