'''
Created on Nov 16, 2021

@author: mballance
'''
from mkdv.runners.runner_make import RunnerMake
from mkdv.runners.runner_gtest import RunnerGtest

class RunnerRgy(object):
    
    _inst = None
    
    def __init__(self):
        self.runner_m = {}
        pass
    
    def get_runner(self, runner_id):
        if runner_id in self.runner_m.keys():
            return self.runner_m[runner_id]
        else:
            return None
    
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = RunnerRgy()
            cls._inst.runner_m["makefile"] = RunnerMake()
            cls._inst.runner_m["gtest"] = RunnerGtest()
            
        return cls._inst
    