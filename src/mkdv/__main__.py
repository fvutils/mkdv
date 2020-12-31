'''
Created on Dec 27, 2020

@author: mballance
'''
import argparse
import os

from mkdv.runner import Runner
from mkdv.test_loader import TestLoader
import asyncio
from _datetime import date, datetime


def mkfile(args):
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(mkdv_dir, "share", "mkfiles", "dv.mk"))
    
def list_tests(args):
    loader = TestLoader()
    specs = loader.load(os.getcwd())
    
    r = Runner(os.getcwd(), specs)

    print("--> run " + str(r))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(r.runjobs())
    print("<-- run")
    
def regress(args):
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
    
    

def get_parser():
    parser = argparse.ArgumentParser(prog="mkdv")
    
    subparser = parser.add_subparsers()
    subparser.required = True
    subparser.dest = 'command'
    
    list_cmd = subparser.add_parser("list",
        help="Discovers and lists available tests")
    list_cmd.set_defaults(func=list_tests)
    
    mkfile_cmd = subparser.add_parser("mkfile",
        help="Returns the path to dv.mk")
    mkfile_cmd.set_defaults(func=mkfile)
    
    regress_cmd = subparser.add_parser("regress",
        help="Run a series of tests")
    regress_cmd.add_argument("-t", "--test-dir")
    regress_cmd.set_defaults(func=regress)    
    
    return parser

def main():
    parser = get_parser()
    
    args = parser.parse_args()

    args.func(args)

if __name__ == "__main__":
    main()
    