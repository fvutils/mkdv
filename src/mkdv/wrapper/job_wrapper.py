'''
Created on Jun 14, 2021

@author: mballance
'''
import os
import subprocess
import allure
import allure_commons
import os

from allure_commons.types import LabelType
from allure_commons.logger import AllureFileLogger
from allure_commons.utils import get_testplan
from allure_commons.reporter import AllureReporter
from allure_commons.utils import uuid4
from allure_commons.utils import now
from allure_commons.model2 import TestResult, Status
from allure_commons.model2 import TestStepResult, TestResult, TestBeforeResult, TestAfterResult


class JobWrapper(object):
    
    def __init__(self, job_yaml):
        self.job_yaml = job_yaml

        job = job_yaml["job"]        
        self.file_logger = AllureFileLogger(job["reportdir"], False)
        allure_commons.plugin_manager.register(self.file_logger)

        self.reporter = AllureReporter()



    
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

        uuid = uuid4()
        test_case = TestResult(uuid=uuid, start=now())
        test_case.name = job["name"]
        test_case.fullname = job["qname"]

        self.reporter.schedule_test(uuid, test_case)

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
            job_log.write(line)
            
        job_log.close()
        
        if proc.wait() == 0:
            test_case.status = Status.PASSED
        else:
            test_case.status = Status.FAILED
            
        self.reporter.attach_file(
            uuid, 
            "job.log",
            "log")
            
        test_case.stop=now()            
        self.reporter.close_test(uuid)
#            print("line: %s" % line)
    
    