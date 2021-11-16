'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
from _datetime import datetime
import os

from mkdv.job_runner import JobRunner
from mkdv.jobspec_loader import JobspecLoader
from mkdv.job_spec_gen_loader import JobSpecGenLoader
from mkdv import backends
from mkdv.job_spec_filter import JobSpecFilter


def cmd_regress(args):
    loader = JobspecLoader()
    
    specfiles = []
    
    if hasattr(args, "jobspec") and args.jobspec is not None:
        specfiles.extend(args.jobspec)
        
    if len(specfiles) == 0:
        if os.path.isfile(os.path.join(os.getcwd(), "mkdv.yaml")):
            specfiles.append(os.path.join(os.getcwd(), "mkdv.yaml"))
        else:
            raise Exception("No specfiles specified")
    
    jobset_s = loader.load_specs(specfiles)

    regress = os.path.join(os.getcwd(), "regress")
    rundir = os.path.join(regress, 
                          datetime.now().strftime("%Y%m%d_%H%M%S"))
    gendir = os.path.join(rundir, "gen")
    
    specs = jobset_s.jobspecs.copy()
    gen_specs = []    
    

    for s in jobset_s.jobspec_gen:
        spec_gendir = os.path.join(gendir, s.root_id)
        os.makedirs(spec_gendir)
        gen_jobset_s = JobSpecGenLoader(spec_gendir).load(s)

        specs.extend(gen_jobset_s.jobspecs)
        
    # filter specs
    specs = JobSpecFilter(
        args.include if args.include is not None else [],
        args.exclude if args.exclude is not None else []
        ).filter(specs)
        
    os.makedirs(rundir, exist_ok=True)
    
    backend = backends.backend(args.backend)
    
    r = JobRunner(rundir, backend, specs)
    
    if hasattr(args, "limit_time") and args.limit_time is not None:
        r.limit_time = args.limit_time
    r.tool = args.tool
    r.rerun_failing = args.rerun_failing

    # TODO: should query the job runner     
    if args.max_par is not None:
        r.maxpar = int(args.max_par)

    print("--> run " + str(r))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(r.runjobs())
    print("<-- run")
