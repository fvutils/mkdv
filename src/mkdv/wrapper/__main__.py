'''
Created on Jun 14, 2021

@author: mballance
'''
import argparse

import yaml
from mkdv.wrapper.job_wrapper import JobWrapper
from mkdv.job_spec import JobSpec
from mkdv.job_yaml_reader import JobYamlReader
import sys


def getparser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("job_yaml")
    
    return parser

def main():
    parser = getparser()

    args = parser.parse_args()

    with open(args.job_yaml, "r") as fp:
        job  = JobSpec.load(fp)
    
    job_w = JobWrapper(job)
    
    try:
        code = job_w.run()
        if code is None:
            code = 1
            print("Error: None returned as exit code", flush=True)
        sys.exit(code)
    except Exception as e:
        sys.exit(1)
    

if __name__ == "__main__":
    main()
    