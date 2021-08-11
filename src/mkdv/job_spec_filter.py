'''
Created on Aug 10, 2021

@author: mballance
'''

class JobSpecFilter(object):
    
    def __init__(self, include, exclude):
        
        self.include = []
        for i in include:
            self.include.append(i.split('.'))
            
        self.exclude = []
        for e in exclude:
            self.exclude.append(e.split('.'))

    
    def filter(self, jobspec_l):
        ret = []
        
        # First, process includes
        if len(self.include) > 0:
            for s in jobspec_l:
                for i in self.include:
                    if self._match(s.fullname, i):
                        ret.append(s)
                        break
        else:
            # No include, so include everything
            ret = jobspec_l.copy()
            
        # Now, process exclusions
        i=0
        while i < len(ret):
            removed = False
            for e in self.exclude:
                if self._match(ret[i].fullname, e):
                    removed = True
                    ret.pop(i)
                    break
            if not removed:
                i += 1
                
        return ret
    
    def _match(self, spec, pattern):
        spec_e = spec.split('.')
        
        match = True
        for i,p in enumerate(pattern):
            if i > len(spec_e):
                match = False
            elif p != spec_e[i]:
                match = False
            
            if not match:
                break
        return match
    