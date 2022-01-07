'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
import os
import sys

from colorama import Fore
from colorama import Style

from mkdv import backends
from .job_spec_set import JobSpecSet
from .jobspec_loader import JobspecLoader
from .job_selector import JobSelector
from .job_queue_builder import JobQueueBuilder
import shutil


def cmd_run(args):
    specs = None
    
    cwd = os.getcwd()
    
    if not os.path.exists(os.path.join(cwd, "mkdv.mk")):
        raise Exception("mkdv.mk does not exist")

    spec = None
        
    specfile = None
    if hasattr(args, "jobspec") and args.jobspec is not None:
        specfile = os.path.abspath(args.jobspec)
     
        if not os.path.exists(specfile):
            raise Exception("Specfile " + specfile + " doesn't exist")
    else:
        if os.path.exists(os.path.join(os.getcwd(), "mkdv.yaml")):
            specfile = os.path.join(os.getcwd(), "mkdv.yaml")
        else:
            raise Exception("Default specfile " + specfile + " doesn't exist")        
      
    loader = JobspecLoader()
    specs : JobSpecSet = loader.load(specfile)
    
    spec_m = {}
    for i,s in enumerate(specs.jobspecs):
        spec_m[s.fullname] = s
              
    if args.jobid in spec_m.keys():
        spec = spec_m[args.jobid]
    else:
        raise Exception("Job-id " + args.jobid + " doesn't exist")
            
    rundir = os.path.join(os.getcwd(), "rundir")
    if os.path.isdir(rundir):
        shutil.rmtree(rundir)
    os.makedirs(rundir, exist_ok=True)
    
    cachedir = os.path.join(os.getcwd(), "cache")
    os.makedirs(cachedir, exist_ok=True)
    
    queue_s = JobQueueBuilder().build([spec])
    queue_s.queues[0].set_cachedir(cachedir)
    
    
    # TODO: remove rundir?
    
    backend = backends.backend(args.backend)

    loop = asyncio.get_event_loop()
    for i,jspec in enumerate(queue_s.queues[0].jobs):
        
        if i == 0:
            print(f"{Fore.YELLOW}[Start Setup]{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[Start Run]{Style.RESET_ALL}")
        sys.stdout.flush()
        
        if i == 0:
            cmd_rundir = cachedir
        else:
            cmd_rundir = rundir
            
        if i > 0:
            jspec.debug = args.debug
            
        cmdline = []
        cmdline.extend([sys.executable, "-m", "mkdv.wrapper"])
        cmdline.append(os.path.join(cmd_rundir, "job.yaml"))
       
        with open(os.path.join(cmd_rundir, "job.yaml"), "w") as fp:
            jspec.dump(fp)
    
        proc = loop.run_until_complete(
            backend.launch(
                jspec,
                cmdline,
                cwd=cmd_rundir))
        
        done,pending = loop.run_until_complete(
            asyncio.wait([loop.create_task(proc.wait())]))

        if proc.returncode == 0:
            if i == 0:
                print(f"{Fore.GREEN}[Setup PASS]{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[Run PASS]{Style.RESET_ALL}")
        else:
            if i == 0:
                print(f"{Fore.RED}[Setup FAIL]{Style.RESET_ALL} -- exit code " + str(proc.returncode))
            else:
                if proc.returncode == 124:
                    print(f"{Fore.RED}[Run Timeout]{Style.RESET_ALL} -- exit code " + str(proc.returncode))
                else:
                    print(f"{Fore.RED}[Run FAIL]{Style.RESET_ALL} -- exit code " + str(proc.returncode))
            return proc.returncode
    
    return 0
