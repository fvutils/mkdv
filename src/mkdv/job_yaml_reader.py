'''
Created on Nov 16, 2021

@author: mballance
'''
import yaml
from mkdv.job_spec import JobSpec


class JobYamlReader(object):
    
    def __init__(self):
        pass
    
    def read(self, s):
        job = JobSpec()
        job_yaml = yaml.load(s, yaml.FullLoader)
        pass