'''
Created on Nov 6, 2021

@author: mballance
'''
import os
import subprocess

from mkdv.job_spec import JobSpec
from mkdv.runners.runner import Runner


class RunnerMake(Runner):
    
    def __init__(self):
        pass

    def validate(self, spec : JobSpec):
        
        if not os.path.isfile(os.path.join(spec.basedir, "mkdv.mk")):
            raise Exception("mkdv.mk doesn't exist")
        pass
    
    def setup(self, spec : JobSpec):
        self.run_job(spec)
    
    def run(self, spec : JobSpec):
        """Runs the specified job. Invoked by the job wrapper"""
        self.run_job(spec)
    
    def run_job(self, spec):
        cmdline = []
        
        mkfile = os.path.join(spec.basedir, "mkdv.mk")
        
#         if "limit-time" in job.keys():
#             cmdline.extend(["timeout", str(job["limit-time"])])
        cmdline.extend(["make", "-f"])
        cmdline.append(mkfile)
        cmdline.append("MKDV_RUNDIR=%s" % os.getcwd())
        cmdline.append("MKDV_CACHEDIR=%s" % spec.cachedir)
        cmdline.append("MKDV_REPORTDIR=%s" % spec.reportdir)
        cmdline.append("MKDV_JOB=%s" % spec.name)
        cmdline.append("MKDV_JOB_QNAME=%s" % spec.fullname)
        cmdline.append("MKDV_JOB_PARENT=" + spec.fullname[0:-(len(spec.name)+1)])

        if spec.is_setup:
            cmdline.append("_setup")
            for k,v in spec.setupvars.items():
                cmdline.append("%s=%s" % (k, v))
        else:
            cmdline.append("_run")
            for k,v in spec.runvars.items():
                cmdline.append("%s=%s" % (k, v))
        
        job_log = open("job.log", "w")
        
        proc = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.decode()
            job_log.write(line)
            
        job_log.close()
        
        code = proc.wait()
        
        if code == 0:
            # Setup jobs don't automatically produce a status.txt
            if spec.is_setup:
                with open("status.txt", "w") as fp:
                    fp.write("PASS: ")
            elif not os.path.isfile("status.txt"):
#                    if test_case is not None:
#                        test_case.status = Status.FAILED
                pass
            else:
                with open("status.txt", "r") as fp:
                    pass_count = 0
                    fail_count = 0
                    for line in fp.readlines():
                        if line.find("PASS") != -1:
                            pass_count += 1
                        if line.find("FAIL") != -1:
                            fail_count += 1

#                    if test_case is not None:
#                        if pass_count > 0 and fail_count == 0:
#                            test_case.status = Status.PASSED
#                        else:
#                            test_case.status = Status.FAILED
        elif code == 124: # Timeout
#            with open("job.log", "a") as fp:
#                fp.write("MKDV Error: Timeout after %s\n" % (
#                    str(job["limit-time"])))
            pass
        else:
#            if test_case is not None:
#                test_case.status = Status.FAILED        
            pass
        
    
    def generate(self):
        """TODO: Invokes appropriate runner-specific mechanism for generating content
           Not all runners need this. Might want a base mechanism that runs 
           the generator inline...
        """
        pass    