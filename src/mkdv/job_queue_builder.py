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

class JobQueueBuilder(object):
    
    def __init__(self):
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
                rq = {j.setupvars : q}
                runner_m[j.runner_spec] = rq
                total_job_l.append(j)
            else:
                rq = runner_m[j.runner_spec]
                if j.setupvars in rq.keys():
                    j.id = len(total_job_l)
                    jq = rq[j.setupvars]
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
                    rq[j.setupvars] = q
                    total_job_l.append(j)

        res = toposort(dep_m)
        print("res-type: %s" % str(type(res)))
        print("Result: %s" % str(list(res)))
        
        return queue_s
        
                
        