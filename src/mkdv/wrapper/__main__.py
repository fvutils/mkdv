'''
Created on Jun 14, 2021

@author: mballance
'''
import argparse

import yaml
from mkdv.wrapper.job_wrapper import JobWrapper


def getparser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("job_yaml")
    
    return parser

def main():
    parser = getparser()

    args = parser.parse_args()

    with open(args.job_yaml, "r") as fp:
        job_yaml = yaml.load(fp, yaml.FullLoader)
    
    job = JobWrapper(job_yaml)
    job.run()
    

if __name__ == "__main__":
    main()
    