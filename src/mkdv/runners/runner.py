'''
Created on Nov 6, 2021

@author: mballance
'''
from typing import List
from mkdv.job_spec import JobSpec
from mkdv.runners.runner_spec import RunnerSpec

class Runner(object):

    def query_jobs(self, job : JobSpec) -> List[JobSpec]:
        """Returns job specifications"""
        return None
    
    def validate(self, spec : JobSpec):
        pass
    
    def setup(self, spec : JobSpec):
        pass
    
    def run(self, spec : JobSpec):
        """Runs the specified job. Invoked by the job wrapper"""
        pass
    
    def generate(self):
        """TODO: Invokes appropriate runner-specific mechanism for generating content
           Not all runners need this. Might want a base mechanism that runs 
           the generator inline...
        """
        pass
    