'''
Created on Apr 13, 2022

@author: mballance
'''

import logging

from pypyr.context import Context
from pypyr import pipelinerunner
import os
import traceback



# getLogger will grab the parent logger context, so your loglevel and
# formatting automatically will inherit correctly from the pypyr core.
logger = logging.getLogger(__name__)

depth = 0

def run_step(context: Context) -> None:
    global depth
    print("run_step")

    # Calculate the path to the directory where the steps file exists
    context["MKDV_JOBDIR"] = os.path.dirname(
        os.path.abspath(
            os.path.join(
                context.current_pipeline.name + ".yaml")))
    context["MKDV_CACHEDIR"] = os.path.join(os.getcwd(), "cache")
    context["MKDV_RUNDIR"] = os.path.join(os.getcwd(), "rundir")

    if depth == 0:
        depth += 1
        print("--> run")
        try:
            ctxt = pipelinerunner.run(
                pipeline_name=context.current_pipeline.name,
                groups=['setup', 'run'],
                dict_in=context,
                py_dir=context.current_pipeline.py_dir)
        except Exception as e:
            print("Exception: %s" % str(e))
            traceback.print_exc()
            raise e
        print("<-- run")
        depth -= 1

    
    # TODO: determine if we're running 