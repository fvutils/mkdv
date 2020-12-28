'''
Created on Dec 27, 2020

@author: mballance
'''
import argparse
import os


def mkfile(args):
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(mkdv_dir, "share", "mkfiles", "dv.mk"))

def get_parser():
    parser = argparse.ArgumentParser(prog="mkdv")
    
    subparser = parser.add_subparsers()
    subparser.required = True
    subparser.dest = 'command'
    
    mkfile_cmd = subparser.add_parser("mkfile",
        help="Returns the path to dv.mk")
    mkfile_cmd.set_defaults(func=mkfile)
    
    return parser

def main():
    parser = get_parser()
    
    args = parser.parse_args()

    args.func(args)

if __name__ == "__main__":
    main()
    