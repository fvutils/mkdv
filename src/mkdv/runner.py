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
from typing import List
from mkdv.job_queue import JobQueue
from mkdv.job_spec import JobSpec

class Runner(object):
    
    def __init__(self, root, specs):
        self.root = root
        self.specs = specs
        self.maxpar = 24
        
    async def runjobs(self):
        loop = asyncio.get_event_loop()
        
        # Ensure each test has a unique name
        name_m = {}
        cache_m = {}
        cache_id = 0
        n_passed = 0
        n_failed = 0

        # Map of mkdv.mk path -> job_queue        
        queue_m = {}

        # Ensure we create the report directory first        
        os.makedirs(os.path.join(self.root, "report"), exist_ok=True)
        
        # Sort specs into the queues
        for s in self.specs:
            if s.mkdv_mk not in queue_m.keys():
                queue_m[s.mkdv_mk] = JobQueue(s.mkdv_mk)
            queue_m[s.mkdv_mk].jobs.append(s)
            
        active_queues = list(queue_m.values())
        
        status = await self.run_builds(active_queues)
        
        if not status:
            return
        
        active_procs = []

        if self.maxpar > 0:
            avail_jobs = self.maxpar
        else:
            # Launch everything
            avail_jobs = len(self.specs)

        # Start         
        spec_i = 0
        queue_i = 0
#        print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))
        while spec_i < len(self.specs) or len(active_procs) > 0:
#            print("spec_i=" + str(spec_i) + " " + str(len(self.specs)))


            # Launch new jobs while there is quota 
            # and            
            while avail_jobs > 0 and spec_i < len(self.specs):
                # Select a spec from one of the queues
                queue = active_queues[queue_i]
                spec = queue.jobs.pop()
                
                if len(queue.jobs) == 0:
                    active_queues.pop(queue_i)

                if len(active_queues) != 0:
                    queue_i = (queue_i+1) % len(active_queues)
                else:
                    queue_i = 0
                
                rundir = os.path.join(self.root, spec.fullname)
                if spec.fullname in name_m.keys():
                    # Need to disambiguate
                    id = name_m[spec.fullname]+1
                    rundir += "_%04d" % (id,)
                    name_m[spec.fullname] = id
                else:
                    name_m[spec.fullname] = 0
                    
                os.makedirs(rundir, exist_ok=True)
               
#                cmdline = ['srun', '-E']
#                cmdline = ['srun', '--nodelist=oatfieldx1,oatfieldx2']
#                cmdline = ['srun']
                cmdline = []
                cmdline.extend([sys.executable, "-m", "mkdv.wrapper"])
                cmdline.append(os.path.join(rundir, "job.yaml"))
                
                self.write_job_yaml(
                    os.path.join(rundir, "job.yaml"),
                    queue.cachedir,
                    spec)

#                 cmdline = ["make"]
#                 cmdline.append("-f")
#                 cmdline.append(spec.mkdv_mk)
#                 cmdline.append("MKDV_RUNDIR=" + rundir)
#                 cmdline.append("MKDV_CACHEDIR=" + queue.cachedir)
#                 cmdline.append("MKDV_TEST=" + spec.localname)
#                 cmdline.append("MKDV_JOB=" + spec.localname)
#                 cmdline.append("MKDV_JOB_QNAME=" + spec.fullname)
#                 cmdline.append("MKDV_JOB_PARENT=" + spec.fullname[0:-(len(spec.localname)+1)])
#                 for v in spec.variables.keys():
#                     cmdline.append(v + "=" + str(spec.variables[v]))
# #                cmdline.append("MKDV_TEST=" + spec.localname)
#                 # TODO: separate build/run
#                 cmdline.append("run")
                spec.rundir = rundir
# 
#                 stdout = open(os.path.join(rundir, "stdout.log"), "w")
# #                stdout = DEVNULL
# #                stdout = None
#                 
# #                print("cmdline: " + str(cmdline))                
                print(f"{Fore.YELLOW}[Start]{Style.RESET_ALL} " + spec.fullname)
                sys.stdout.flush()
#                 proc = await asyncio.subprocess.create_subprocess_exec(
#                     *cmdline,
#                     cwd=rundir,
#                     stderr=STDOUT,
#                     stdout=stdout)

                proc = await asyncio.subprocess.create_subprocess_exec(
                    *cmdline,
                    cwd=rundir)
                
#                print("proc=" + str(proc))
                
#                active_procs.append((proc,spec,stdout))
                active_procs.append((proc,spec,None))
                
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
                    if p[2] is not None:
                        p[2].close() # Close stdout save
                    if os.path.isfile(os.path.join(p[1].rundir, "status.txt")):
                        is_passed,msg = self.checkstatus(os.path.join(p[1].rundir, "status.txt"))
                        
                        if is_passed:
                            print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} " + p[1].fullname + " - " + msg)
                            n_passed += 1
                        else:
                            print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} " + p[1].fullname + " - " + msg)
                            n_failed += 1
                        pass
                    else:
                        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} " + p[1].fullname + " - no status.txt")
                        n_failed += 1
                    sys.stdout.flush()
                    avail_jobs += 1

        print()                    
        print()                    
        print(f"{Fore.YELLOW}[Run ]{Style.RESET_ALL} " + str(n_passed+n_failed))
        print(f"{Fore.GREEN}[Pass]{Style.RESET_ALL} " + str(n_passed))
        print(f"{Fore.RED}[Fail]{Style.RESET_ALL} " + str(n_failed))
        
    def write_job_yaml(
            self, 
            job_yaml,
            cachedir,
            spec : JobSpec):
        
        with open(job_yaml, "w") as fp:
            fp.write("job:\n");
            fp.write("    mkfile: %s\n" % spec.mkdv_mk)
            fp.write("    cachedir: %s\n" % cachedir)
            fp.write("    reportdir: %s\n" % os.path.join(self.root, "report"))
            fp.write("    name: %s\n" % spec.localname)
            fp.write("    qname: %s\n" % spec.fullname)
            if len(spec.variables) > 0:
                fp.write("    variables:\n")
                for v in spec.variables.keys():
                    fp.write("        %s: \"%s\"\n" % (v, spec.variables[v]))
            if spec.description is not None:
                fp.write("    description: |\n")
                for line in spec.description.split("\n"):
                    fp.write("        %s\n" % line)

            if len(spec.labels) > 0:
                fp.write("    labels:\n")
                for key in spec.labels.keys():
                    fp.write("        - %s: %s\n" % (key, spec.labels[key]))
                    
            if len(spec.parameters) > 0:
                fp.write("    parameters:\n")
                for key in spec.parameters.keys():
                    fp.write("        - %s: %s\n" % (key, spec.parameters[key]))

            if len(spec.attachments) > 0:
                fp.write("    attachments:\n")
                for a in spec.attachments:
                    fp.write("    - %s: %s\n" % (a[0], a[1]))
            
#            fp.write("    rundir: %s\n" % rundir)spec.mkdv_mk)
#                 cmdline.append("-f")
#                 cmdline.append(spec.mkdv_mk)
#                 cmdline.append("MKDV_RUNDIR=" + rundir)
#                 cmdline.append("MKDV_CACHEDIR=" + queue.cachedir)
#                 cmdline.append("MKDV_TEST=" + spec.localname)
#                 cmdline.append("MKDV_JOB=" + spec.localname)
#                 cmdline.append("MKDV_JOB_QNAME=" + spec.fullname)
#                 cmdline.append("MKDV_JOB_PARENT=" + spec.fullname[0:-(len(spec.localname)+1)])
#                 for v in spec.variables.keys():
#                     cmdline.append(v + "=" + str(spec.variables[v]))
# #                cmdline.append("MKDV_TEST=" + spec.localname)
#                 # TODO: separate build/run
#                 cmdline.append("run")            
                    
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
                cmdline.append("build")

                stdout = open(os.path.join(job.cachedir, "stdout.log"), "w")
#                stdout = DEVNULL
#                stdout = None
                
#                print("cmdline: " + str(cmdline))                
                print(f"{Fore.YELLOW}[Start Build]{Style.RESET_ALL} " + job.mkdv_mk)
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
                        print(f"{Fore.GREEN}[Build PASS]{Style.RESET_ALL} " + p[1].mkdv_mk)
                    else:
                        build_fails += 1
                        print(f"{Fore.RED}[Build FAIL]{Style.RESET_ALL} " + p[1].mkdv_mk + " -- exit code " + str(p[0].returncode))
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
            
