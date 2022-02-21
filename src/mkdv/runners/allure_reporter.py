'''
Created on Nov 16, 2021

@author: mballance
'''
from allure_commons.logger import AllureFileLogger
import allure_commons
from mkdv.job_spec import JobSpec
from allure_commons.utils import uuid4, now
from allure_commons.types import LabelType
import socket
from allure_commons.model2 import Parameter, Status, TestResult, Label

class AllureReporter(object):
    
    def __init__(self, job : JobSpec):
        self.job = job
        if not job.rerun and not job.is_setup:
            self.file_logger = AllureFileLogger(job.reportdir, False)
            allure_commons.plugin_manager.register(self.file_logger)
        
            self.reporter = allure_commons.reporter.AllureReporter()
        else:
            # Don't record re-run jobs, since these are just
            # done to get extra log data
            self.reporter = None
        
        self.test_uuid = None
        self.test_case = None
        pass
    
    def start(self):
        if self.reporter is None:
            return

        self.test_uuid = uuid4()
        self.test_case = TestResult(uuid=self.test_uuid, start=now())
        self.test_case.fullname = self.job.fullname

        self._build_testcase_name()
        
        if self.job.description is not None:
            self.test_case.description = self.job.description

        self.reporter.schedule_test(self.test_uuid, self.test_case)
        
        pass
    
    def done(self, status : Status, job_log=None):
        if self.reporter is None:
            return
        
        self.test_case.status = status
        
        self.test_case.labels.append(Label(name=LabelType.FRAMEWORK, value=self.job.tool))
        self.test_case.labels.append(Label(name=LabelType.HOST, value=socket.gethostname()))
        self.test_case.parameters.append(Parameter(name="TOOL", value=self.job.tool))
        
        for l in self.job.labels:
            self.test_case.labels.append(Label(name=l[0], value=l[1]))
        for p in self.job.parameters:
            self.test_case.parameters.append(Parameter(name=p[0], value=p[1]))

        # Record the run variables as test parameters            
        for k,v in self.job.runvars.items():
            self.test_case.parameters.append(Parameter(name=k, value=v))
        
        # Record the seed as a test parameter
        self.test_case.parameters.append(Parameter(name="SEED", value=str(self.job.seed)))
            
        if job_log is not None:
            self.reporter.attach_file(
                uuid4(),
                job_log,
                "job.log")
        for a in self.job.attachments:
            pass
        
        self.test_case.stop = now()
        self.reporter.close_test(self.test_uuid)
        
        pass
    
    def _build_testcase_name(self):
        elems = self.job.fullname.split('.')
        
        if len(elems) > 4:
            # When we more elements in the qualified name than
            # will fit in the PARENT::SUITE::SUBSUITE scheme.
            #
            # We do a bit of middle compression to maximize 
            # readability. 

            collapse_root = True

            if collapse_root:
                # Collapse leaf elements

                root = ""
                for i,e in enumerate(elems[:-4]):
                    if i > 0:
                        root += "."
                    root += e

#                print("root=%s suite=%s sub_suite=%s" % (root, elems[-3], elems[-2]))
                self.test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=root))
                self.test_case.labels.append(Label(name=LabelType.SUITE, value=elems[-3]))
                self.test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[-2]))
                self.test_case.name = elems[-1]
            else:
                # Collapse leaf elements
                self.test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=elems[0]))
                self.test_case.labels.append(Label(name=LabelType.SUITE, value=elems[1]))
                self.test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[2]))

                subsuite = ""
                for i,e in enumerate(elems[3:]):
                    if i > 0:
                        subsuite += "."
                    subsuite += e
                self.test_case.name = subsuite
        else:
            self.test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=elems[0]))

            if len(elems) > 1:
                self.test_case.labels.append(Label(name=LabelType.SUITE, value=elems[1]))

            if len(elems) > 2:
                self.test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[2]))
            self.test_case.name = self.job.name
    
    
    
    