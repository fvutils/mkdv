'''
Created on Nov 7, 2021

@author: mballance
'''
from copy import deepcopy


class JobLimitSpec(object):
    
    def __init__(self):
        self.time = None
        
    def __eq__(self, other):
        if not isinstance(other, JobLimitSpec):
            return False
        
        ret = True
        ret &= ((self.time is None and other.time is None) or (self.time == other.time))
        
        return ret
    
    def copy(self):
        return deepcopy(self)
    
    def dump(self):
        ret = {}
        ret["time"] = self.time
        return ret
    
    def load(self, limit_s):
        if "time" in limit_s.keys():
            self.time = limit_s["time"]
            
        