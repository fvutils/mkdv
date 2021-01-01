'''
Created on Dec 30, 2020

@author: mballance
'''

import asyncio
import multiprocessing
import os
import subprocess
import sys
from asyncio.subprocess import DEVNULL, STDOUT
from asyncio.tasks import FIRST_COMPLETED
from colorama import Fore
from colorama import Style

class Runner(object):
    
    def __init__(self, root, specs):
        self.root = root
        self.specs = specs
        self.maxpar = 20
        
    async def runjobs(self):
        loop = asyncio.get_event_loop()
        
        # Ensure each test has a unique name
        name_m = {}
        cache_m = {}
        cache_id = 0
        
        active_procs = []

        if self.maxpar > 0:
            avail_jobs = self.maxpar
        else:
            # Launch everything
            avail_jobs = len(self.specs)

        # Start         
        spec_i = 0
#        print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))
        while spec_i < len(self.specs):
#            print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))

            # Launch new jobs while there is quota 
            # and            
            while avail_jobs > 0 and spec_i < len(self.specs):
                spec = self.specs[spec_i]

                rundir = os.path.join(self.root, spec.fullname)
                if spec.fullname in name_m.keys():
                    # Need to disambiguate
                    id = name_m[spec.fullname]+1
                    rundir += "_%04d" % (id,)
                    name_m[spec.fullname] = id
                else:
                    name_m[spec.fullname] = 0

                if spec.mkdv_mk in cache_m.keys():
                    id = cache_m[spec.mkdv_mk]
                    cachedir = os.path.join(self.root, "cache_" + str(id))
                else:
                    cachedir = os.path.join(self.root, "cache_" + str(cache_id))
                    cache_m[spec.mkdv_mk] = cache_id
                    cache_id += 1

                os.makedirs(rundir, exist_ok=True)

                cmdline = ["make"]
                cmdline.append("-f")
                cmdline.append(spec.mkdv_mk)
                cmdline.append("MKDV_RUNDIR=" + rundir)
                cmdline.append("MKDV_CACHEDIR=" + rundir)
                cmdline.append("run")
                spec.rundir = rundir

                stdout = open(os.path.join(rundir, "stdout.log"), "w")
#                stdout = DEVNULL
#                stdout = None
                
#                print("cmdline: " + str(cmdline))                
                print(f"{Fore.GREEN}[Start]{Style.RESET_ALL} " + spec.fullname)
                sys.stdout.flush()
                proc = await asyncio.subprocess.create_subprocess_exec(
                    *cmdline,
                    cwd=rundir,
                    stderr=STDOUT,
                    stdout=stdout)
                
#                print("proc=" + str(proc))
                
                active_procs.append((proc,spec,stdout))
                
                spec_i += 1
                avail_jobs -= 1
            
            # Wait for at least once job to complete            
            done, pending = await asyncio.wait(
                [loop.create_task(p[0].wait()) for p in active_procs],
                return_when=FIRST_COMPLETED)
#            print("done=" + str(done) + " pending=" + str(pending))
            
            old_active_procs = active_procs
            active_procs = []
            
            for p in old_active_procs:
                if p[0].returncode is None:
                    active_procs.append(p)
                else:
                    p[2].close() # Close stdout save
                    if os.path.isfile(os.path.join(p[1].rundir, "status.txt")):
                        # TOOD: go figure out what happened
                        print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} " + p[1].fullname + " - no status.txt")
                        pass
                    else:
                        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} " + p[1].fullname + " - no status.txt")
                    sys.stdout.flush()
                    avail_jobs += 1
                
        