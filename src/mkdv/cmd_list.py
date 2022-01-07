'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
import os

from mkdv.jobspec_loader import JobspecLoader
from mkdv.job_spec_set import JobSpecSet


def cmd_list(args):

    specfile = None
    if hasattr(args, "jobspec") and args.jobspec is not None:
        specfile = os.path.abspath(args.jobspec)
        
        if not os.path.exists(specfile):
            raise Exception("Specfile " + specfile + " doesn't exist")
    else:
        specfile = os.path.join(os.getcwd(), "mkdv.yaml")
        
        if not os.path.exists(specfile):
            raise Exception("Default specfile " + specfile + " doesn't exist")

    loader = JobspecLoader()
    specs : JobSpecSet = loader.load(specfile)

    jobid_l = [spec.fullname for spec in specs.jobspecs]
    jobid_l.sort()
   
    if args.categories:
        categories = []
        for j in jobid_l:
            last_dot = j.rfind(".")
            if last_dot != -1:
                short = j[0:last_dot]
                if short not in categories:
                    categories.append(short)
            else:
                categories.append(j)

        for c in categories:                
            print("%s" % c)
    else:
        # Show all jobs
        for j in jobid_l:
            print("%s" % j)
        
def show_jobids(jobid_l, list_idx, jobid_idx_s, ind_s) -> int:
    print("--> show_jobids")
    check_last = False
    while list_idx < len(jobid_l):
        jobid_idx = jobid_idx_s[-1]
        curr_jobid = jobid_l[list_idx]
        curr_prefix = curr_jobid[0:jobid_idx]
        
        print("curr_jobid: %s curr_prefix: %s" % (curr_jobid, curr_prefix))
        
#        if list_idx > 0 and not jobid_l[list_idx-1].startswith(curr_prefix):
#            return list_idx
        if list_idx+1 < len(jobid_l):
            # See if we can build a longer prefix before moving on
            next_jobid = jobid_l[list_idx+1]
            print("  next_jobid: %s" % next_jobid)
           
            if next_jobid.startswith(curr_prefix):
                nd_idx = curr_jobid.find('.', jobid_idx)
                if nd_idx != -1 and next_jobid.startswith(curr_jobid[0:nd_idx]):
                    ind_s.append(ind_s[-1] + "    ")
                    jobid_idx_s.append(nd_idx+1)
                    list_idx = show_jobids(
                        jobid_l, 
                        list_idx, 
                        jobid_idx_s,
                        ind_s)
                    ind_s.pop()
                    jobid_idx_s.pop()
                    check_last = True
                else:
                    print_jobid(curr_jobid, jobid_idx, ind_s[-1])
                    list_idx += 1
                    check_last = True
            else:
                # The next one doesn't even start with this prefix.
                # Display this jobid and bail out.
                print_jobid(curr_jobid, jobid_idx, ind_s[-1])
                list_idx += 1
                return list_idx
        else:
            # This is the last element. In this case, we need
            # to check the previous element
            if list_idx > 0:
                if jobid_l[list_idx-1].startswith(curr_prefix):
                    print_jobid(curr_jobid, jobid_idx, ind_s[-1])
                    list_idx += 1
                else:
                    return list_idx
            else:
                print_jobid(curr_jobid, jobid_idx, ind_s[-1])
                list_idx += 1
    print("<-- show_jobids")
    pass

def print_jobid(jobid, jobid_idx, ind):
    print("%s%s" % (ind, jobid[jobid_idx:]))

