'''
Created on Feb 20, 2021

@author: mballance
'''
import asyncio
from _datetime import datetime
import os

from .runner import Runner
from .test_loader import TestLoader


def cmd_regress(args):
    loader = TestLoader()
    specs = loader.load(os.getcwd())

    regress = os.path.join(os.getcwd(), "regress")
    rundir = os.path.join(regress, 
                          datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    os.makedirs(rundir, exist_ok=True)
    
    r = Runner(rundir, specs)

    print("--> run " + str(r))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(r.runjobs())
    print("<-- run")