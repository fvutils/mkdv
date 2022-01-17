'''
Created on May 28, 2021

@author: mballance
'''
from mkdv.job_spec_gen import JobSpecGen
from mkdv.jobspec_loader import JobspecLoader
import os
import subprocess
import sys


class JobSpecGenLoader(object):
    
    def __init__(self, rundir):
        self.rundir = rundir
        pass

    def load(self, spec : JobSpecGen):
        if not os.path.isdir(self.rundir):
            os.makedirs(self.rundir)

        with open(os.path.join(self.rundir, "cmd.sh"), "w") as fp:
            fp.write("#!/bin/sh\n")
            fp.write("set -e\n")
            fp.write(spec.cmd)
        
        os.chmod(
            os.path.join(self.rundir, "cmd.sh"),
            0o755)
            
        # TODO: how do we know which shell?
        
        env = os.environ.copy()
        env["MKDV_MK_DIR"] = os.path.dirname(spec.mkdv_mk)
        env["MKDV_MK_JOBID"] = spec.root_id
            
        ret = subprocess.run(
            "./cmd.sh",
            cwd=self.rundir,
            shell="/bin/bash",
            env=env)
        
        if ret.returncode != 0:
            raise Exception("Job-spec generation command failed")
        
        if not os.path.isfile(os.path.join(self.rundir, spec.path)):
            raise Exception(
                "Expected to find generated jobspec file \"%s\"" % spec.path)
            
        jobset_s = JobspecLoader().load(
            self.rundir,
            specfile=os.path.join(self.rundir, spec.path),
            dflt_mkdv_mk=spec.mkdv_mk,
            prefix=spec.root_id)

        return jobset_s        
        
        