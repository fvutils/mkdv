'''
Created on Dec 27, 2020

@author: mballance
'''
import argparse
import os

import asyncio
from .cmd_list import cmd_list
from .cmd_regress import cmd_regress
from .cmd_run import cmd_run
import sys
from mkdv.jobspec_loader import JobspecLoader
from mkdv import backends
from mkdv.cmd_files import cmd_files
from mkdv.cmd_filespec import cmd_filespec


def mkfile(args):
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(mkdv_dir, "share", "mkfiles", "dv.mk"))
    
def list_tests(args):
    loader = JobspecLoader()
    specs = loader.load(os.getcwd())
    
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
    list_cmd.add_argument("-s", "--job-spec", dest="jobspec", action="append",
        help="Specifies the job-spec file (mkdv.yaml by default)")
    list_cmd.add_argument("-c", "--job-categories", dest="categories",
        action="store_true", help="Show job categories, not individual jobs")
    list_cmd.set_defaults(func=cmd_list)
    
    files_cmd = subparser.add_parser("files",
        help="Returns files referenced by a specific core target")
    files_cmd.add_argument("-i", "--include",
        action="store_true", 
        help="Report include paths instead of file paths")
    files_cmd.add_argument("-l", "--library-path",
        dest="library_path", action="append",
        help="Specifies a library path")
    files_cmd.add_argument("-e", "--target",
        dest="target",
        help="Specifies the entry target (default if not specified)")
    files_cmd.add_argument("-f", "--flag",
        dest="flags", action="append",
        help="Specifies a flag to be applied")
    files_cmd.add_argument("-t", "--file-type",
        dest="file_type", action="append",
        help="Specifies the file-type identifier to query")
    files_cmd.add_argument("vlnv",
        help="Specifies the identifier of the core to query")
    files_cmd.set_defaults(func=cmd_files)
    
    filespec_cmd = subparser.add_parser("filespec",
        help="Extracts files based on a filespec and writes to a file")
    filespec_cmd.add_argument("-d", "--debug",
        action="store_true", help="Enables debug")
    filespec_cmd.add_argument("-o", "--output",
        help="Specifies the output file")
    filespec_cmd.add_argument("-l", "--library-path",
        dest="library_path", action="append",
        help="Specifies a library path")
    filespec_cmd.add_argument("-t", "--template",
        help="Specifies the template to use for output")
    filespec_cmd.add_argument("filespec", help="Specifies YAML filespec")
    filespec_cmd.set_defaults(func=cmd_filespec)
    
    mkfile_cmd = subparser.add_parser("mkfile",
        help="Returns the path to dv.mk")
    mkfile_cmd.set_defaults(func=mkfile)
    
    regress_cmd = subparser.add_parser("regress",
        help="Run a series of tests")
    regress_cmd.add_argument("-l", "--library-path", 
        dest="library_path", action="append",
        help="Specifies a directory containing libraries specified via .core files")
    regress_cmd.add_argument("-s", "--job-spec", 
        dest="jobspecs", action="append",
        help="Specifies a file containing a test-spec to use")
    regress_cmd.add_argument("-t", "--tool", dest="tool",
        help="Specify the tool to run (defaults to makefile setting)")
    regress_cmd.add_argument("-j", "--max-par", dest="max_par",
        help="Specifies maximum jobs to run in parallel")
    regress_cmd.add_argument("-b", "--backend", dest="backend",
        default="local", choices=backends.backends(),
        help="Specifies the backend used for launching jobs")
    regress_cmd.add_argument("-e", "--exclude", dest="exclude",
        action="append", 
        help="Specifies test patterns to exclude from the runlist")
    regress_cmd.add_argument("-i", "--include", dest="include",
        action="append", 
        help="Specifies test patterns to include in the runlist")
    regress_cmd.add_argument("-lt", "--limit-time", dest="limit_time",
        help="Specify job's time limit")
    regress_cmd.add_argument("-r", "--rerun-failing", dest="rerun_failing",
        action="store_true",
        help="Rerun failing jobs with debug enabled")
    
    regress_cmd.set_defaults(func=cmd_regress)
    
    run_cmd = subparser.add_parser("run",
        help="Run a single job")
    run_cmd.add_argument("-t", "--tool", dest="tool",
        help="Specify the tool to run (defaults to makefile setting)")
    run_cmd.add_argument("-d", "--debug", dest="debug",
        action="store_true",
        help="Run in debug mode")
    run_cmd.add_argument("-lt", "--limit-time", dest="limit_time",
        help="Specify job's time limit")
    run_cmd.add_argument("-b", "--backend", dest="backend",
        default="local", choices=backends.backends(),
        help="Specifies the backend used for launching jobs")
    run_cmd.add_argument("-s", "--job-spec", dest="jobspec",
        help="Specifies the job-spec file (mkdv.yaml by default)")
    run_cmd.add_argument("jobid", help="Specifies job-id to run.")
    run_cmd.set_defaults(func=cmd_run)
    
    return parser

def main():
    from .mkdv_py import in_main
    
    in_main()
    parser = get_parser()
    
    args = parser.parse_args()

    status = args.func(args)
    
    if status is not None:
        sys.exit(status)

if __name__ == "__main__":
    main()
    
