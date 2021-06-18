'''
Created on Jun 14, 2021

@author: mballance
'''
import os
import os
import subprocess
from typing import Dict, List, Tuple

import allure
import allure_commons
from allure_commons.logger import AllureFileLogger
from allure_commons.model2 import TestResult, Status, TestStepResult
from allure_commons.model2 import TestStepResult, TestResult, TestBeforeResult, TestAfterResult
from allure_commons.reporter import AllureReporter
from allure_commons.types import LabelType
from allure_commons.utils import get_testplan
from allure_commons.utils import now
from allure_commons.utils import uuid4


class JobWrapper(object):
    
    def __init__(self, job_yaml):
        self.job_yaml = job_yaml

        job = job_yaml["job"]        
        self.file_logger = AllureFileLogger(job["reportdir"], False)
        allure_commons.plugin_manager.register(self.file_logger)

        self.reporter = AllureReporter()
        self.step_m : Dict[str, List[Tuple[str,TestStepResult]]] = {}



    
    def run(self):
        job = self.job_yaml["job"]
    
        cmdline = ["make", "-f"]
        cmdline.append(job["mkfile"].strip())
        cmdline.append("MKDV_RUNDIR=%s" % os.getcwd())
        cmdline.append("MKDV_CACHEDIR=%s" % job["cachedir"].strip())
        cmdline.append("MKDV_REPORTDIR=%s" % job["reportdir"].strip())
        qname = job["qname"].strip()
        localname = job["name"].strip()
        cmdline.append("MKDV_JOB=%s" % localname)
        cmdline.append("MKDV_JOB_QNAME=%s" % qname)
        cmdline.append("MKDV_JOB_PARENT=" + qname[0:-(len(localname)+1)])
    
        if "variables" in job.keys():
            variables = job["variables"]
            for v in variables.keys():
                value = variables[v]
                if value[0] == '"':
                    value = value[1:-2]
                cmdline.append("%s=%s" % (v, value))
                
        job_log = open("job.log", "w")

        test_uuid = uuid4()
        test_case = TestResult(uuid=test_uuid, start=now())
        test_case.name = job["name"]
        test_case.fullname = job["qname"]
        if "description" in job.keys():
            test_case.description = job["description"]

        self.reporter.schedule_test(test_uuid, test_case)

# step1_uuid = uuid4()
# step = TestStepResult(name="My Step", start=now(), parameters=[])
# logger.start_step(None, step1_uuid, step)
# step2_uuid = uuid4()
# step = TestStepResult(name="My Substep", start=now(), parameters=[])
# logger.start_step(step1_uuid, step2_uuid, step)
# logger.stop_step(step2_uuid, stop=now())
# #logger.stop_step(step1_uuid, stop=now())

#        test_result = self.reporterlogger.get_test(None)
#        test_result.descriptionHtml = "Hello World"

                
        proc = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
           
            line = line.decode()
            if line[0] == '@' and line.startswith("@step"):
                if line.startswith("@step-begin"):
                    begin = len("@step-begin")
                    end = -1
                    
                    while begin < len(line) and line[begin].isspace():
                        begin += 1
                    end = begin + 1
                    while end < len(line) and not line[end].isspace():
                        end += 1
                    
                    key = line[begin:end]
                    
                    if key not in self.step_m.keys():
                        root = TestStepResult(name=key)
                        uuid = uuid4()
                        self.reporter.start_step(None, uuid, root)
                        self.step_m[key] = [(uuid, root)]
                    step_s = self.step_m[key]
                   
                    parent_uuid = None if len(step_s) == 0 else step_s[-1][0]
                    uuid = uuid4()

                    step = TestStepResult(name=line[end+1:])
                    step_s.append((uuid, step))
                    self.reporter.start_step(parent_uuid, uuid, step)
                  
                elif line.startswith("@step-end"):
                    begin = len("@step-end")
                    end = -1
                    
                    while begin < len(line) and line[begin].isspace():
                        begin += 1
                    end = begin + 1
                    while end < len(line) and not line[end].isspace():
                        end += 1
                    
                    key = line[begin:end]
                    
                    if key not in self.step_m.keys():
                        self.step_m[key] = []
                    step_s = self.step_m[key]
                    
                    if len(step_s) == 0:
                        print("Warning: unmatched step-end")
                    else:
                        uuid, step = step_s.pop()
                        step.status = Status.PASSED
                        self.reporter.stop_step(uuid, stop=now())

            job_log.write(line)
            
        job_log.close()
        
        # Close out remaining steps
        for key in self.step_m.keys():
            for step_i in self.step_m[key]:
                step_i[1].status = Status.PASSED
                self.reporter.stop_step(step_i[0], stop=now())
        
        if proc.wait() == 0:
            test_case.status = Status.PASSED
        else:
            test_case.status = Status.FAILED
            
        self.reporter.attach_file(
            test_uuid, 
            "job.log",
            "log")
            
        test_case.stop=now()
        self.reporter.close_test(test_uuid)
#            print("line: %s" % line)
    
    