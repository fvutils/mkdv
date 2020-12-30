'''
Created on Dec 30, 2020

@author: mballance
'''

import multiprocessing
import subprocess
import asyncio
from asyncio.tasks import FIRST_COMPLETED
from asyncio.subprocess import DEVNULL, STDOUT

class Runner(object):
    
    def __init__(self, root, specs):
        print("Runner::__init__")
        self.root = root
        self.specs = specs
        self.maxpar = 1
        
    async def runjobs(self):
        print("run")
        
        loop = asyncio.get_event_loop()
        
        active_procs = []

        if self.maxpar > 0:
            avail_jobs = self.maxpar
        else:
            # Launch everything
            avail_jobs = len(self.specs)

        # Start         
        spec_i = 0
        print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))
        while spec_i < len(self.specs):
            print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))

            # Launch new jobs while there is quota 
            # and            
            while avail_jobs > 0 and spec_i < len(self.specs):
                cmdline = ["make"]
                cmdline.append("-f")
                cmdline.append(self.specs[spec_i].mkdv_mk)
                cmdline.append("run")

                print("cmdline: " + str(cmdline))                
                proc = await asyncio.subprocess.create_subprocess_exec(
                    *cmdline,
                    stderr=STDOUT,
                    stdout=DEVNULL)
                
                print("proc=" + str(proc))
                
                active_procs.append(proc)
                
                spec_i += 1
                avail_jobs -= 1
            
            # Check for completed jobs
#             print("--> wait")
#             await active_procs[0].wait()
#             avail_jobs += 1
#             active_procs.clear()
#             print("<-- wait")

            # Wait for at least once job to complete            
            done, pending = await asyncio.wait(
                [loop.create_task(p.wait()) for p in active_procs],
                return_when=FIRST_COMPLETED)
            print("done=" + str(done) + " pending=" + str(pending))
            
            old_active_procs = active_procs
            active_procs = []
            
            for p in old_active_procs:
                if p.returncode is None:
                    active_procs.append(p)
                else:
                    avail_jobs += 1
                
        