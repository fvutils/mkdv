'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
import os
import sys

from colorama import Fore
from colorama import Style

from mkdv.job_spec_set import JobSpecSet
from mkdv.jobspec_loader import JobspecLoader


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
    specs : JobSpecSet = loader.load(
        os.path.dirname(specfile),
         specfile)
    
    spec_m = {}
    for s in specs.jobspecs:
        spec_m[s.fullname] = s
              
    if args.jobid in spec_m.keys():
        spec = spec_m[args.jobid]
    else:
        raise Exception("Job-id " + args.jobid + " doesn't exist")
            
    print("spec=" + str(spec))
    
    cmdline = []
    
    cmdline.append("make")
    cmdline.append("-f")
    cmdline.append(os.path.join(cwd, "mkdv.mk"))

    # Add variables    
    if spec is not None:
        spec.append_run_variables(cmdline)
    
    if hasattr(args, "tool") and args.tool is not None:
        cmdline.append("MKDV_TOOL=" + args.tool)
        
    if hasattr(args, "debug") and args.debug:
        cmdline.append("MKDV_DEBUG=1")
        cmdline.append("DEBUG=1")
        
    for var,val in spec.variables.items():
        cmdline.append("%s=\"%s\"" % (var, val))
        
    
    # TODO: Add variables if spec

    cmdline.append("_setup")

    print(f"{Fore.YELLOW}[Start Setup]{Style.RESET_ALL}")
    sys.stdout.flush()
    loop = asyncio.get_event_loop()    
    proc = loop.run_until_complete(
        asyncio.subprocess.create_subprocess_exec(*cmdline))
    
    done,pending = loop.run_until_complete(
        asyncio.wait([loop.create_task(proc.wait())]))

    if proc.returncode == 0:
        print(f"{Fore.GREEN}[Setup PASS]{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[Setup FAIL]{Style.RESET_ALL} -- exit code " + str(proc.returncode))
        return proc.returncode
        
    cmdline.pop()
    
    if hasattr(args, "limit_time") and args.limit_time is not None:
        cmdline.insert(0, "%s" % args.limit_time)
        cmdline.insert(0, "timeout")
    cmdline.append("_run")
    
    print(f"{Fore.YELLOW}[Start Run]{Style.RESET_ALL}")
    sys.stdout.flush()
    loop = asyncio.get_event_loop()    
    proc = loop.run_until_complete(
        asyncio.subprocess.create_subprocess_exec(*cmdline))
    
    done,pending = loop.run_until_complete(
        asyncio.wait([loop.create_task(proc.wait())]))
    print("<-- run")

    if proc.returncode == 0:
        print(f"{Fore.GREEN}[Run PASS]{Style.RESET_ALL}")
    elif proc.returncode == 124:
        print(f"{Fore.RED}[Run FAIL]{Style.RESET_ALL} timeout after %s" % str(args.limit_time))
    else:
        print(f"{Fore.RED}[Run FAIL]{Style.RESET_ALL} -- exit code " + str(proc.returncode))
        
    return proc.returncode
        
#    loop = asyncio.get_event_loop()    
    
#    loader = TestLoader()
#    specs = loader.load(os.getcwd())
#    pass