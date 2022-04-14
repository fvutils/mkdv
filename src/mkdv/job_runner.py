'''
Created on Dec 30, 2020

@author: mballance
'''

import asyncio
import datetime
import multiprocessing
import os
import subprocess
import sys
from asyncio.subprocess import DEVNULL, STDOUT
from asyncio.tasks import FIRST_COMPLETED
from colorama import Fore
from colorama import Style
from typing import List
from mkdv.job_queue import JobQueue
from mkdv.job_spec import JobSpec
from mkdv.job_queue_builder import JobQueueBuilder
from mkdv.job_yaml_writer import JobYamlWriter
from mkdv.job_selector import JobSelector

class JobRunner(object):
    
    def __init__(self, root, backend, specs):
        self.root = root
        self.backend = backend
        self.specs = specs
        self.maxpar = -1
        self.rerun_failing = True
        self.limit_time = None
        self.tool = None
        self.debug = False
        
    async def runjobs(self):
        start = datetime.datetime.now()
        loop = asyncio.get_event_loop()
        
        # Ensure each test has a unique name
        name_m = {}
        n_passed = 0
        n_failed = 0

        # Build the job queues based on required setup jobs
        queue_s = JobQueueBuilder().build(self.specs)
        
        # Ensure we create the report directory first        
        os.makedirs(os.path.join(self.root, "report"), exist_ok=True)
        
        # Populate the cachedir of each queue and job
        for i,q in enumerate(queue_s.queues):
            q.set_cachedir(os.path.join(self.root, "cache_%d" % i))
            q.set_reportdir(os.path.join(self.root, "report"))
        
        active_procs = []

        if self.maxpar == -1:
            avail_jobs = self.backend.quota()
        else:
            avail_jobs = self.maxpar
        
        if self.debug:    
            print("maxpar: %d %d" % (self.maxpar, avail_jobs))
        
        selector = JobSelector(queue_s)

        while selector.avail() or len(active_procs) > 0:

            # Launch new jobs while there is quota 
            # and            
            while (avail_jobs == -1 or len(active_procs) < avail_jobs) and selector.avail():
                # TODO: could randomize selection
                spec = selector.next()

                if spec is not None:
                    if spec.rundir is None:
                        rundir = os.path.join(self.root, spec.fullname)
                        if spec.fullname in name_m.keys():
                            # Need to disambiguate
                            id = name_m[spec.fullname]+1
                            rundir += "_%04d" % (id,)
                            name_m[spec.fullname] = id
                        else:
                            name_m[spec.fullname] = 0
                        
                        spec.rundir = rundir
                        
                    os.makedirs(spec.rundir, exist_ok=True)
                   
                    cmdline = []
                    cmdline.extend([sys.executable, "-m", "mkdv.wrapper"])
                    cmdline.append(os.path.join(rundir, "job.yaml"))
                    
                    self.init_spec(spec)

                    with open(os.path.join(rundir, "job.yaml"), "w") as fp:
                        spec.dump(fp)
    
                    if spec.rerun:
                        print(f"{Fore.YELLOW}[Start]{Style.RESET_ALL} %s (rerun)" % spec.fullname)
                    else:
                        if spec.is_setup:
                            print(f"{Fore.YELLOW}[StartSetup]{Style.RESET_ALL} %s" % spec.basedir)
                        else:
                            print(f"{Fore.YELLOW}[Start]{Style.RESET_ALL} %s" % spec.fullname)
                    sys.stdout.flush()
    
                    proc = await self.backend.launch(
                        spec,
                        cmdline,
                        cwd=spec.rundir)
                    
                    active_procs.append((proc,spec,None))
                else:
                    # Need to wait for some jobs to complete
                    break
                
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
                    if p[2] is not None:
                        p[2].close() # Close stdout save

                    spec = p[1]
                    selector.complete(spec)
                    if os.path.isfile(os.path.join(p[1].rundir, "status.txt")):
                        is_passed,msg = self.checkstatus(os.path.join(p[1].rundir, "status.txt"))
                        
                        if is_passed:
                            if spec.is_setup:
                                print(f"{Fore.GREEN}[PASSSetup]{Style.RESET_ALL} %s" % p[1].basedir)
                            else:
                                print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} " + p[1].fullname + " - " + msg)
                            n_passed += 1
                        else:
                            if spec.rerun and not spec.is_setup:
                                print(f"{Fore.YELLOW}[ExpFail]{Style.RESET_ALL} " + p[1].fullname + " - " + msg + " (rerun)")
                            else:
                                print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} " + p[1].fullname + " - " + msg)
                                # Number of failures shouldn't be bumped for re-runs
                                n_failed += 1
                            
                            if self.rerun_failing:
                                # Determine whether we need to rerun with debug
                                if not "MKDV_DEBUG" in spec.variables.keys() or spec.variables["MKDV_DEBUG"] != "1":
                                    print(f"{Fore.YELLOW}[QueueDebugRerun]{Style.RESET_ALL} " + spec.fullname)
                                    spec.variables["MKDV_DEBUG"] = "1"
                                    # Add a '_dbg' suffix
                                    spec.rundir += "_dbg"
                                    spec.rerun = True
                                    selector.rerun(spec)
                        pass
                    else:
                        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} " + p[1].fullname + " - no status.txt")
                        n_failed += 1
                    sys.stdout.flush()

        end = datetime.datetime.now()
        duration = end - start
        print()                    
        print()                    
        print(f"{Fore.YELLOW}[Run ]{Style.RESET_ALL} " + str(n_passed+n_failed))
        print(f"{Fore.GREEN}[Pass]{Style.RESET_ALL} " + str(n_passed))
        print(f"{Fore.RED}[Fail]{Style.RESET_ALL} " + str(n_failed))
        tv = str(duration)
        tv = tv[0:tv.rfind('.')]
        print(f"{Fore.YELLOW}[Time]{Style.RESET_ALL} %s" % tv)
        
    def init_spec(self, spec : JobSpec):
#        if "MKDV_TOOL" not in spec.variables.keys() and self.tool is not None:
#            spec.variables["MKDV_TOOL"] = str(self.tool)
        pass
            
    async def run_builds(self, jobs : List[JobQueue]):
        loop = asyncio.get_event_loop()
        build_fails = 0
        
        # Start         
        queue_i = 0
        active_procs = []
        
        if self.maxpar > 0:
            avail_jobs = self.maxpar
        else:
            # Launch everything
            avail_jobs = len(jobs)
        
#        print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))
        while queue_i < len(jobs) or len(active_procs) > 0:
#            print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))

            # Launch new jobs while there is quota 
            # and            
            while avail_jobs > 0 and queue_i < len(jobs):
                job = jobs[queue_i]

                job.cachedir = os.path.join(self.root, "cache_" + str(queue_i))
                os.makedirs(job.cachedir, exist_ok=True)

                cmdline = ["make"]
                cmdline.append("-f")
                cmdline.append(job.mkdv_mk)
                cmdline.append("MKDV_RUNDIR=" + job.cachedir)
                cmdline.append("MKDV_CACHEDIR=" + job.cachedir)
                # TODO: separate build/run
                cmdline.append("_setup")

                stdout = open(os.path.join(job.cachedir, "stdout.log"), "w")
#                stdout = DEVNULL
#                stdout = None
                
#                print("cmdline: " + str(cmdline))                
                print(f"{Fore.YELLOW}[Start Setup]{Style.RESET_ALL} " + job.mkdv_mk)
                sys.stdout.flush()
                proc = await asyncio.subprocess.create_subprocess_exec(
                    *cmdline,
                    cwd=job.cachedir,
                    stderr=STDOUT,
                    stdout=stdout)
                
#                print("proc=" + str(proc))
                
                active_procs.append((proc,job,stdout))
                
                queue_i += 1
                avail_jobs -= 1
            
            # Wait for at least once job to complete            
            done, pending = await asyncio.wait(
                [loop.create_task(p[0].wait()) for p in active_procs],
                return_when=FIRST_COMPLETED)
            
            old_active_procs = active_procs
            active_procs = []
            
            for p in old_active_procs:
                if p[0].returncode is None:
                    active_procs.append(p)
                else:
                    p[2].close() # Close stdout save
                    if p[0].returncode == 0:
                        print(f"{Fore.GREEN}[Setup PASS]{Style.RESET_ALL} " + p[1].mkdv_mk)
                    else:
                        build_fails += 1
                        print(f"{Fore.RED}[Setup FAIL]{Style.RESET_ALL} " + p[1].mkdv_mk + " -- exit code " + str(p[0].returncode))
                    sys.stdout.flush()
                    avail_jobs += 1        
                    
        return build_fails == 0
                
       
    def checkstatus(self, status_txt):
        have_pass = False
        have_fail = False
        msg = ""
        with open(status_txt, "r") as fp:
            for l in fp.readlines():
                if l.startswith("PASS:"):
                    have_pass = True
                    msg = l[len("PASS:"):].strip()
                    break
                elif l.startswith("FAIL:"):
                    have_fail = True
                    msg = l[len("FAIL:"):].strip()
                    break

        if not have_pass and not have_fail:
            return (False,"no PASS or FAIL")
        else:
            return ((have_pass and not have_fail),msg)
            
