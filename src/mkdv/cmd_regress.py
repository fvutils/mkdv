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
from mkdv import backends, get_packages_dir
from mkdv.job_spec_filter import JobSpecFilter
from mkdv.job_count_expander import JobCountExpander
from mkdv.core_manager_w import CoreManagerW
from fusesoc.librarymanager import Library


def cmd_regress(args):
    
    specfiles = []
    
    cm = CoreManagerW()
    
    packages_dir = get_packages_dir()
    project_dir = os.path.dirname(packages_dir)
    cm.add_library(Library("project", project_dir))
    
    cwd_is_lib = False
    if args.library_path is not None:
        for path in args.library_path:
            if os.getcwd().startswith(path):
                cwd_is_lib = True
            cm.add_library(Library(os.path.basename(path), path))
        
    if not cwd_is_lib:
        cm.add_library(Library(os.path.basename(os.getcwd()), os.getcwd()))

    if hasattr(args, "jobspecs") and args.jobspecs is not None:
        specfiles.extend(args.jobspecs)
        
    if len(specfiles) == 0:
        if os.path.isfile(os.path.join(os.getcwd(), "mkdv.yaml")):
            specfiles.append(os.path.join(os.getcwd(), "mkdv.yaml"))
        else:
            raise Exception("No specfiles specified")
        
    loader = JobspecLoader(core_mgr=cm)
    
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
        
    # Expand any jobs that have a count >1
    specs_exp = JobCountExpander.expand(specs)
    
    # Now, assign each unique job an id and seed
    for i,s in enumerate(specs_exp):
        s.id = i
        s.seed = i
        
    os.makedirs(rundir, exist_ok=True)
    
    backend = backends.backend(args.backend)
    
    r = JobRunner(rundir, backend, specs_exp)
    
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
