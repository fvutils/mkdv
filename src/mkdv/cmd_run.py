'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
import os

from .test_loader import TestLoader


def cmd_run(args):
    specs = []
    
    cwd = os.getcwd()
    
    if not os.path.exists(os.path.join(cwd, "mkdv.mk")):
        raise Exception("mkdv.mk does not exist")

    spec = None
        
    if hasattr(args, "jobid") and args.jobid is not None:
        # Need to load job-specs
        
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
        
        loader = TestLoader()
        specs = loader.load(
            os.path.dirname(specfile),
            specfile)
            
        spec_m = {}
        for s in specs:
            spec_m[s.fullname] = s
                
        if args.jobid in spec_m.keys():
            spec = spec_m[args.jobid]
        else:
            raise Exception("Job-id " + args.jobid + " doesn't exist")
            
    print("spec=" + str(spec))
    
    cmdline = ["make"]
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
    
    # TODO: Add variables if spec

    cmdline.append("run")

    print("--> run")
    loop = asyncio.get_event_loop()    
    proc = loop.run_until_complete(
        asyncio.subprocess.create_subprocess_exec(*cmdline))
    
    done,pending = loop.run_until_complete(
        asyncio.wait([loop.create_task(proc.wait())]))

    return proc.returncode
        
    print("<-- run")
#    loop = asyncio.get_event_loop()    
    
#    loader = TestLoader()
#    specs = loader.load(os.getcwd())
#    pass