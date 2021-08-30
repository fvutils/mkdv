'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
from _datetime import datetime
import os

from .runner import Runner
from mkdv.jobspec_loader import JobspecLoader
from mkdv.job_spec_gen_loader import JobSpecGenLoader
from mkdv import backends


def cmd_regress(args):
    loader = JobspecLoader()
    jobset_s = loader.load(os.getcwd())

    regress = os.path.join(os.getcwd(), "regress")
    rundir = os.path.join(regress, 
                          datetime.now().strftime("%Y%m%d_%H%M%S"))
    gendir = os.path.join(rundir, "gen")
    
    specs = jobset_s.jobspecs.copy()
    gen_specs = []    
    # TODO: filter specs

    for s in jobset_s.jobspec_gen:
        spec_gendir = os.path.join(gendir, s.root_id)
        os.makedirs(spec_gendir)
        gen_jobset_s = JobSpecGenLoader(spec_gendir).load(s)

        specs.extend(gen_jobset_s.jobspecs)
        
    os.makedirs(rundir, exist_ok=True)
    
    backend = backends.backend(args.backend)
    
    r = Runner(rundir, backend, specs)

    # TODO: should query the job runner     
    if args.max_par is not None:
        r.maxpar = int(args.max_par)

    print("--> run " + str(r))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(r.runjobs())
    print("<-- run")
