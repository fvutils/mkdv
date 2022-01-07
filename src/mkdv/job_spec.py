'''
Created on Dec 30, 2020

@author: mballance
'''
from typing import Tuple, List, Dict, Set
from mkdv.runners.runner_spec import RunnerSpec
from mkdv.job_vars import JobVars
import yaml
from mkdv.job_limit_spec import JobLimitSpec

class JobSpec(object):
    
    def __init__(self, name, fullname):
        
        # Name is what the user specified
        self.name = name

        # Fullname encodes the full path within the
        # job suite, as well as an index for jobs
        # run multiple times        
        self.fullname = fullname

        # Numeric identifier for the job
        self.id = 0
        
        self.seed = 0

        # A >1 count comes from the testlist        
        self.count = 1
        
        self.debug = False
        
        self.is_setup = False
        self.rerun = False
        
        self.description = None
        
        self.tool = None
       
        # Directory containing the job specification
        self.basedir = None
        
        # Run directory is populated late
        self.rundir = None

        # Cache directory is populated once jobs are known        
        self.cachedir = None
        
        # Directory in which Allure reports are placed
        self.reportdir = None
        
        self.setupvars = JobVars()
        
        self.runvars = JobVars()
        
        self.setup_generators = {}
        
        self.run_generators = {}
        
        # Attachments, parameters, and labels are used by 
        # the runner to determine what data to save for reporting        
        self.attachments : List[Tuple[str, str]] = []
        self.parameters : Dict[str,str] = {}
        self.labels : Dict[str,str] = {}

        # Rerun specifies whether this job execution is a rerun
        # of a previous unsuccessful run
                
        self.limit = None
        
        # Runner spec contains data about *how* to execute the job
        self.runner_spec : RunnerSpec = None
        
    def add_parameter(self, key, val, append=False):
        if key in self.parameters.keys() and append:
            self.parameters[key] += val
        else:
            self.parameters[key] = val
            
    def add_label(self, key, val, append=False):
        if key in self.labels.keys() and append:
            self.labels[key] += val
        else:
            self.labels[key] = val
            
    def dump(self, s):
        job_s = {}

        job_s["id"]        = self.id
        job_s["seed"]      = self.seed        
        job_s["name"]      = self.name
        job_s["debug"]     = self.debug
        job_s["fullname"]  = self.fullname
        job_s["is-setup"] = self.is_setup
        job_s["rerun"] = self.rerun
        job_s["description"] = self.description
        job_s["tool"] = self.tool
        job_s["basedir"] = self.basedir
        job_s["rundir"] = self.rundir
        job_s["cachedir"] = self.cachedir
        job_s["reportdir"] = self.reportdir
        
        setupvars_s = {}
        for k,v in self.setupvars.items():
            setupvars_s[k] = v
        job_s["setupvars"] = setupvars_s
        
        runvars_s = {}
        for k,v in self.runvars.items():
            runvars_s[k] = v
        job_s["runvars"] = runvars_s
        
        if self.limit is None:
            job_s["limit"] = None
        else:
            job_s["limit"] = self.limit.dump()
        
        runner_s = {}
        runner_s["runner-id"] = self.runner_spec.runner_id
        runner_s["config"] = self.runner_spec.config
        job_s["runner-spec"] = runner_s
                
        
        job = {"job" : job_s}
        
        yaml.dump(job, s)        

    @staticmethod
    def load(s) -> 'JobSpec':
        job_yaml = yaml.load(s, yaml.FullLoader)
        job_s = job_yaml["job"]
        job = JobSpec(job_s["name"], job_s["fullname"])
        
        job.id = job_s["id"]
        job.seed = job_s["seed"]
        
        job.debug = job_s["debug"]
        job.is_setup = job_s["is-setup"]
        job.rerun = job_s["rerun"]
        job.description = job_s["description"]
        job.tool = job_s["tool"]
        job.basedir = job_s["basedir"]
        job.rundir = job_s["rundir"]
        job.cachedir = job_s["cachedir"]
        job.reportdir = job_s["reportdir"]
        
        setupvars_s = job_s["setupvars"]
        for k,v in setupvars_s.items():
            job.setupvars[k] = v
        runvars_s = job_s["runvars"]
        for k,v in runvars_s.items():
            job.runvars[k] = v

        runner_s = job_s["runner-spec"]
        job.runner_spec = RunnerSpec(runner_s["runner-id"])
        job.runner_spec.config = runner_s["config"]
        
        if "limit" in job_s.keys() and job_s["limit"] is not None:
            job_s.limit = JobLimitSpec()
            job_s.limit.load(job_s["limit"])
        
        return job
    
    

