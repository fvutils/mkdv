'''
Created on Nov 23, 2021

@author: mballance
'''
import os
import subprocess
from typing import List

from mkdv.job_spec import JobSpec
from mkdv.runners.allure_reporter import AllureReporter
from mkdv.runners.runner import Runner
from mkdv.runners.runner_spec import RunnerSpec
from allure_commons.model2 import Status
from copy import deepcopy

class RunnerGtest(Runner):
    
    def __init__(self):
        pass
    
    def query_jobs(self, job:JobSpec)->List[JobSpec]:
        if "exe-path" not in job.runner_spec.config.keys():
            raise Exception("Expect 'exe-path' entry in runner config")
        
        exe_path = job.runner_spec.config["exe-path"]

        exe = None
        if not isinstance(exe_path, list):
            exe_path = [exe_path]
            
        for try_e in exe_path:
            if os.path.isfile(os.path.join(job.basedir, try_e)):
                exe = os.path.join(job.basedir, try_e)
                break
        
        if exe is None:
            raise Exception("Failed to find gtest executable")

        # Pass forward just the resolved path        
        job.runner_spec.config["exe-path"] = exe
        
        cmdline = [exe, "--gtest_list_tests"]
        
        proc = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        
        print("name: %s" % job.name)
        print("fullname: %s" % job.fullname)

        ret = []
        prefix = None        
        while True:
            line = proc.stdout.readline()
            
            if not line:
                break

            line = line.decode()            
            line = line.strip()
            
            if line[-1] == '.':
                prefix = line
            else:
                name = prefix + line
                j = deepcopy(job)
                j.name = name
                j.fullname = job.fullname + "." + name
                print("Fullname: %s" % j.fullname)
                ret.append(j)
        
        return ret
    
    def setup(self, spec:JobSpec):
        pass
    
    def run(self, spec:JobSpec):
        cmdline = []
        
        reporter = AllureReporter(spec)
        
        if spec.limit is not None and spec.limit.time is not None:
            cmdline.extend(["timeout", spec.limit.time])

        exe = spec.runner_spec.config["exe-path"]
        cmdline.extend([exe, "--gtest_filter=%s" % spec.name])
        
        job_log = open("job.log", "w")

        reporter.start()        
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

        status = None        
        if code == 0:
            with open("status.txt", "w") as fp:
                fp.write("PASS: ")
            status = Status.PASSED
        elif code == 124: # Timeout
            with open("job.log", "a") as fp:
                fp.write("MKDV Error: Timeout after %s\n" % (str(spec.limit.time)))
        else:
            status = Status.FAILED
        
        reporter.done(status, 
                      os.path.join(os.getcwd(), "job.log"))
        
        if code != 0:
            return 1
        else:
            return 0
        
        