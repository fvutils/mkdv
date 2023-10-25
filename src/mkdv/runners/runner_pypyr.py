#****************************************************************************
#* runner_pypyr.py
#*
#* Copyright 2022 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import logging
import os
import subprocess
import traceback

from mkdv.job_spec import JobSpec
from mkdv.runners.runner import Runner
from mkdv.runners.allure_reporter import AllureReporter
from pypyr.context import Context
import pypyr.log.logger
from pypyr import pipelinerunner
from allure_commons.model2 import Status

logger = logging.getLogger(__name__)

class RunnerPypyr(object):

    def __init__(self):
        pass

    def validate(self, spec : JobSpec):
        
        if not os.path.isfile(os.path.join(spec.basedir, "mkdv.yaml")):
            raise Exception("mkdv.yaml doesn't exist")
        pass

    def setup(self, spec : JobSpec):

        context = self._mkContext(spec)

        try:
            ctxt = pipelinerunner.run(
                pipeline_name=os.path.join(spec.basedir, "mkdv"),
                groups=['setup'],
                dict_in=context,
                py_dir=spec.basedir)
        except Exception as e:
            print("Exception: %s" % str(e))
            traceback.print_exc()
            raise e
        
        return 0
    
    def run(self, spec : JobSpec):
        """Runs the specified job. Invoked by the job wrapper"""
        context = self._mkContext(spec)

#        pypyr.log.logger.set_root_logger(
#            log_level=10
#        )

        try:
            ctxt = pipelinerunner.run(
                pipeline_name=os.path.join(spec.basedir, "mkdv"),
                groups=['run'],
                dict_in=context,
                py_dir=spec.basedir)
        except Exception as e:
            print("Exception: %s" % str(e))
            traceback.print_exc()
            raise e
        
        return 0
        
    def _mkContext(self, spec):
        context = Context()

        context["MKDV_JOBDIR"] = spec.basedir
        context["MKDV_CACHEDIR"] = os.path.join(os.getcwd(), "cache")
        context["MKDV_RUNDIR"] = os.path.join(os.getcwd(), "rundir")
#        context["MKDV_TOOL"] = spec.tool

        if "MKDV_RUN_ARGS" in context.keys():
            args = context["MKDV_RUN_ARGS"]
            if type(args) is str:
                args_l = []
                args_l.extend(args.split(" "))
                context["MKDV_RUN_ARGS"] = args_l

        return context
    
    def run_job(self, spec):
        cmdline = []

        if spec.reportdir is not None:
            reporter = AllureReporter(spec)
        else:
            reporter = None
        
        mkfile = os.path.join(spec.basedir, "mkdv.mk")
       
        if spec.limit is not None and spec.limit.time is not None:
            cmdline.extend(["timeout", spec.limit.time])
#         if "limit-time" in job.keys():
        cmdline.extend(["make", "-f"])
        cmdline.append(mkfile)
        cmdline.append("MKDV_RUNDIR=%s" % os.getcwd())
        cmdline.append("MKDV_CACHEDIR=%s" % spec.cachedir)
        cmdline.append("MKDV_REPORTDIR=%s" % spec.reportdir)
        cmdline.append("MKDV_JOB=%s" % spec.name)
        cmdline.append("MKDV_JOB_QNAME=%s" % spec.fullname)
        cmdline.append("MKDV_JOB_PARENT=" + spec.fullname[0:-(len(spec.name)+1)])
        cmdline.append("MKDV_SEED=%d" % spec.seed)
        
        if spec.tool is not None:
            cmdline.append("MKDV_TOOL=%s" % spec.tool)
        
        if spec.debug:
            cmdline.append("MKDV_DEBUG=1")

        if spec.is_setup:
            for k,v in spec.setupvars.items():
                cmdline.append("%s=%s" % (k, v))
            cmdline.append("_setup")
        else:
            for k,v in spec.runvars.items():
                cmdline.append("%s=%s" % (k, v))
            cmdline.append("_run")

        job_log = open("job.log", "w")

        if reporter is not None:
            reporter.start()        
        proc = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.decode()
            job_log.write(line)
        
        code = proc.wait()

        job_log.flush()
        job_log.close()
        os.sync()

        cmdline[-1] = "_check"
        result = subprocess.run(
                cmdline,
                stdout=subprocess.DEVNULL)

        status = None        
        if result.returncode == 0:
            # Setup jobs don't automatically produce a status.txt
            if spec.is_setup:
                with open("status.txt", "w") as fp:
                    fp.write("PASS: ")
            elif not os.path.isfile("status.txt"):
                status = Status.FAILED
            else:
                with open("status.txt", "r") as fp:
                    pass_count = 0
                    fail_count = 0
                    for line in fp.readlines():
                        if line.find("PASS") != -1:
                            pass_count += 1
                        if line.find("FAIL") != -1:
                            fail_count += 1

#                    if test_case is not None:
                    if pass_count > 0 and fail_count == 0:
                        status = Status.PASSED
                    else:
                        status = Status.FAILED
        elif code == 124: # Timeout
            with open("job.log", "a") as fp:
                fp.write("MKDV Error: Timeout after %s\n" % (str(spec.limit.time)))
        else:
            status = Status.FAILED        

        if reporter is not None:        
            reporter.done(status, 
                    os.path.join(os.getcwd(), "job.log"))
        
        if code != 0:
            return 1
        else:
            return 0
        
    
    def generate(self):
        """TODO: Invokes appropriate runner-specific mechanism for generating content
           Not all runners need this. Might want a base mechanism that runs 
           the generator inline...
        """
        pass    


