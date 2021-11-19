'''
Created on Nov 16, 2021

@author: mballance
'''
from allure_commons.logger import AllureFileLogger
import allure_commons
from mkdv.job_spec import JobSpec

class AllureReporter(object):
    
    def __init__(self, reportdir, job : JobSpec):
        self.file_logger = AllureFileLogger(reportdir, False)
        allure_commons.plugin_manager.register(self.file_logger)
        
        self.reporter = AllureReporter()
        pass
    
    def start(self):
        pass
    
    def done(self, status=None):
        pass
    
    
    
    