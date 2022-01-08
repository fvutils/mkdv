'''
Created on Nov 9, 2021

@author: mballance
'''
from typing import List, Dict
from mkdv.job_spec import JobSpec
from mkdv.job_queue import JobQueue
from mkdv.runners.runner_spec import RunnerSpec
from copy import deepcopy
from simplesat.utils.graph import toposort
from mkdv.job_queue_set import JobQueueSet

class JobSetupW(object):
    
    def __init__(self, js):
        self.js = js
        
    def __hash__(self):
        ret = 0
        for key,val in self.js.setupvars.items():
            ret += hash(key)
            if isinstance(val, list):
                for it in list:
                    ret += hash(it)
            else:
                ret += hash(val)
        if self.js.tool is not None:
            ret += hash(self.js.tool)

        return ret
    
    def __eq__(self, other):
        if not isinstance(other, JobSetupW):
            return False
        
        eq = (self.js.tool is None and other.js.tool is None) or (self.js.tool == other.js.tool)
        eq &= self.js.setupvars == other.js.setupvars
        
        return eq

class JobQueueBuilder(object):
    
    def __init__(self):
        self.debug = 0
        pass
    
    def build(self, specs : List[JobSpec]) -> JobQueueSet:
        """Organizes the jobs by runner and setup variables"""
        
        runner_m : Dict[RunnerSpec, Dict[Dict[str,str],JobQueue]] = {}
        queue_s = JobQueueSet()

        dep_m = {}
        total_job_l = []
        for j in specs:
            if j.runner_spec not in runner_m.keys():
                setup_j = deepcopy(j)
                setup_j.is_setup = True
                setup_j.id = len(total_job_l)
                total_job_l.append(setup_j)
                j.id = len(total_job_l)
                dep_m[j.id] = {setup_j.id}
                q = JobQueue()
                q.append(setup_j)
                q.append(j)
                queue_s.queues.append(q)
                rq = {JobSetupW(j) : q}
                runner_m[j.runner_spec] = rq
                total_job_l.append(j)
            else:
                rq = runner_m[j.runner_spec]
                jsw = JobSetupW(j)
                if jsw in rq.keys():
                    j.id = len(total_job_l)
                    jq = rq[jsw]
                    dep_m[j.id] = {jq.jobs[0].id}
                    jq.append(j)
                    total_job_l.append(j)
                else:
                    # TODO: Create a dedicated setup job (?)
                    setup_j = deepcopy(j)
                    setup_j.is_setup = True
                    setup_j.id = len(total_job_l)
                    total_job_l.append(setup_j)
                    j.id = len(total_job_l)
                    dep_m[j.id] = {setup_j.id}
                    q = JobQueue()
                    q.append(setup_j)
                    q.append(j)
                    queue_s.queues.append(q)
                    rq[jsw] = q
                    total_job_l.append(j)

        res = toposort(dep_m)
        
        if self.debug > 0:
            print("res-type: %s" % str(type(res)))
            print("Result: %s" % str(list(res)))
        
        return queue_s
        
                
        