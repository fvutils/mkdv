'''
Created on Nov 15, 2021

@author: mballance
'''
from mkdv.job_queue_set import JobQueueSet
from mkdv.job_spec import JobSpec

class JobSelector(object):
    
    def __init__(self, queue_s : JobQueueSet):
        self.queue_s = queue_s
        self.queue_idx = [0]*len(queue_s.queues)
        self.queue_dep_s = []
        for _ in queue_s.queues:
            self.queue_dep_s.append(set())
        self.rerun_q = []
        
    def avail(self) -> bool:
        ret = False
        for i,q in enumerate(self.queue_s.queues):
            if self.queue_idx[i] < len(q.jobs):
                ret = True
                break
            
        return ret
    
    def rerun(self, j):
        self.rerun_q.insert(0, j)
    
    def next(self) -> JobSpec:
        job = None
        
        if len(self.rerun_q) > 0:
            job = self.rerun_q.pop()
        else:
            for i,q in enumerate(self.queue_s.queues):
                if len(self.queue_dep_s[i]) == 0:
                    if self.queue_idx[i] < len(q.jobs):
                        job = q.jobs[self.queue_idx[i]]
                        
                        if self.queue_idx[i] == 0:
                            self.queue_dep_s[i].add(job)
                        self.queue_idx[i] += 1
                        
                if job is not None:
                    break
            
        return job
    
    def complete(self, j : JobSpec):
        for i,d in enumerate(self.queue_dep_s):
            if j in d:
                d.remove(j)
                
                # TODO: invalidate dependent jobs
                
                
            
        
