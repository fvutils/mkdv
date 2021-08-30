'''
Created on Jul 16, 2021

@author: mballance
'''
import asyncio
from mkdv.backends.backend import Backend
import multiprocessing


class BackendLocal(Backend):
    
    def __init__(self):
        pass
    
    def quota(self):
        """Returns the max parallel jobs to launch"""
        return multiprocessing.cpu_count()
    
    async def launch(self, cmdline, cwd=None):
        """Launches a new job and returns a proxy process"""
        
        proc = await asyncio.subprocess.create_subprocess_exec( 
            *cmdline, cwd=cwd)
        
        return proc
    