'''
Created on Apr 13, 2022

@author: mballance
'''

from runpy import run_module
import importlib
from pypyr.context import Context
import sys
import subprocess
import traceback
from io import StringIO

def run_step(context : Context):
    
    context.assert_key_exists("cmd", "run_step")
    cmd_r = context.get_formatted("cmd")
    
    print("cmd=%s" % cmd_r)
    
    cmd_l = cmd_r.split()
    print("cmd_l=%s" % str(cmd_l))

    cmd = [sys.executable, '-m']
    cmd.extend(cmd_l)
    
    if "out" in context.keys():
        try:
            out = subprocess.check_output(cmd)
        except Exception as e:
            print("Exception: %s" % str(e))
            traceback.print_exc()
            raise e
        context[context["out"]] = out.decode().strip()
    else:
        try:
            subprocess.run(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr)
        except Exception as e:
            raise e

    pass