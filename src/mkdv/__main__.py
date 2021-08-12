'''
Created on Dec 27, 2020

@author: mballance
'''
import argparse
import os

from mkdv.runner import Runner
import asyncio
from .cmd_list import cmd_list
from .cmd_regress import cmd_regress
from .cmd_run import cmd_run
import sys
from mkdv.jobspec_loader import JobspecLoader


def mkfile(args):
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(mkdv_dir, "share", "mkfiles", "dv.mk"))
    
def list_tests(args):
    loader = JobspecLoader()
    specs = loader.load(os.getcwd())
    
    r = Runner(os.getcwd(), specs)

    print("--> run " + str(r))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(r.runjobs())
    print("<-- run")
    
   
def run(args):
    loader = JobspecLoader()
    specs = loader.load(os.getcwd())
   
    pass
    

def get_parser():
    parser = argparse.ArgumentParser(prog="mkdv")
    
    subparser = parser.add_subparsers()
    subparser.required = True
    subparser.dest = 'command'
    
    list_cmd = subparser.add_parser("list",
        help="Discovers and lists available tests")
    list_cmd.add_argument("-s", "--job-spec", dest="jobspec",
        help="Specifies the job-spec file (mkdv.yaml by default)")
    list_cmd.add_argument("-c", "--job-categories", dest="categories",
        action="store_true", help="Show job categories, not individual jobs")
    list_cmd.set_defaults(func=cmd_list)
    
    mkfile_cmd = subparser.add_parser("mkfile",
        help="Returns the path to dv.mk")
    mkfile_cmd.set_defaults(func=mkfile)
    
    regress_cmd = subparser.add_parser("regress",
        help="Run a series of tests")
    regress_cmd.add_argument("-t", "--test-spec", 
        dest="test_specs", action="append",
        help="Specifies a file containing a test-spec to use")
    regress_cmd.add_argument("-j", "--max-par", dest="max_par",
        help="Specifies maximum jobs to run in parallel")
    regress_cmd.add_argument("-e", "--exclude", dest="exclude",
        action="append", 
        help="Specifies test patterns to exclude from the runlist")
    regress_cmd.add_argument("-i", "--include", dest="include",
        action="append", 
        help="Specifies test patterns to include in the runlist")
    regress_cmd.set_defaults(func=cmd_regress)
    
    run_cmd = subparser.add_parser("run",
        help="Run a single job")
    run_cmd.add_argument("-t", "--tool", dest="tool",
        help="Specify the tool to run (defaults to makefile setting)")
    run_cmd.add_argument("-d", "--debug", dest="debug",
        action="store_true",
        help="Run in debug mode")
    run_cmd.add_argument("-s", "--job-spec", dest="jobspec",
        help="Specifies the job-spec file (mkdv.yaml by default)")
    run_cmd.add_argument("jobid", help="Specifies job-id to run.")
    run_cmd.set_defaults(func=cmd_run)
    
    return parser

def main():
    parser = get_parser()
    
    args = parser.parse_args()

    status = args.func(args)
    
    if status is not None:
        sys.exit(status)

if __name__ == "__main__":
    main()
    