'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
import os

from .runner import Runner
from .test_loader import TestLoader


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

    loader = TestLoader()
    specs = loader.load(
        os.path.dirname(specfile),
        specfile)
    
    for s in specs:
        print("JobId: " + s.fullname)
    
#    r = Runner(os.getcwd(), specs)

#    print("--> run " + str(r))
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(r.runjobs()) 

