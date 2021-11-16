'''
Created on Nov 15, 2021

@author: mballance
'''

class JobVars(dict):
    
    def __init__(self):
        super().__init__()
        
    def __hash__(self, *args, **kwargs):
        ret = 0
        for key,val in self.items():
            ret += hash(key)
            if isinstance(val, list):
                for it in list:
                    ret += hash(it)
            else:
                ret += hash(val)
        return ret
    