'''
Created on Nov 23, 2021

@author: mballance
'''
from typing import List
from mkdv.job_spec import JobSpec
from copy import deepcopy

class JobCountExpander(object):

    @staticmethod    
    def expand(specs : List[JobSpec]) -> List[JobSpec]:
        ret = []
        
        for s in specs:
            if s.count == 1:
                ret.append(s)
            else:
                for i in range(s.count):
                    s_c = deepcopy(s)
                    s_c.fullname = "%s.%04d" % (s.fullname, i)
                    ret.append(s_c)

        print("CountExpander: in=%d out=%d" % (len(specs), len(ret)))                    
        return ret
    