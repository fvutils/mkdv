'''
Created on Jun 14, 2021

@author: mballance
'''
import os
import socket
import subprocess
from typing import Dict, List, Tuple

import allure
import allure_commons
from allure_commons.logger import AllureFileLogger
from allure_commons.model2 import TestResult, Status, TestStepResult, Label,\
    Parameter, StatusDetails
from allure_commons.model2 import TestStepResult, TestResult, TestBeforeResult, TestAfterResult
from allure_commons.reporter import AllureReporter
from allure_commons.types import LabelType
from allure_commons.utils import get_testplan
from allure_commons.utils import now
from allure_commons.utils import uuid4
from mkdv.runners.runner_rgy import RunnerRgy



class JobWrapper(object):
    
    def __init__(self, job):
        self.job = job

        # self.file_logger = AllureFileLogger(job["reportdir"], False)
        # allure_commons.plugin_manager.register(self.file_logger)
        #
        # self.reporter = AllureReporter()
        # self.step_stream_m = Dict[str, List]
        # self.step_m : Dict[str, List[Tuple[str,TestStepResult]]] = {}
    
    def run(self):
        runner_rgy = RunnerRgy.inst()
        
        runner = runner_rgy.get_runner(self.job.runner_spec.runner_id)
        
        if runner is None:
            raise Exception("Failed to find runner %s" % self.job.runner_spec.runner_id)
        
        runner.validate(self.job)
        
        if self.job.is_setup:
            return runner.setup(self.job)
        else:
            return runner.run(self.job)
        
#         cmdline = []
#         if "limit-time" in job.keys():
#             cmdline.extend(["timeout", str(job["limit-time"])])
#         cmdline.extend(["make", "-f"])
#         cmdline.append(job["mkfile"].strip())
#         cmdline.append("MKDV_RUNDIR=%s" % os.getcwd())
#         cmdline.append("MKDV_CACHEDIR=%s" % job["cachedir"].strip())
#         cmdline.append("MKDV_REPORTDIR=%s" % job["reportdir"].strip())
#         qname = job["qname"].strip()
#         localname = job["name"].strip()
#         cmdline.append("MKDV_JOB=%s" % localname)
#         cmdline.append("MKDV_JOB_QNAME=%s" % qname)
#         cmdline.append("MKDV_JOB_PARENT=" + qname[0:-(len(localname)+1)])
#
#         if self.job_yaml["is-setup"]:
#             cmdline.append("_setup")
#         else:
#             cmdline.append("_run")
#
#         rerun = job["rerun"]
#
#         if "variables" in job.keys():
#             variables = job["variables"]
#             for v in variables.keys():
#                 value = variables[v]
#                 if value[0] == '"':
#                     value = value[1:-2]
#                 cmdline.append("%s=%s" % (v, value))
#
#         job_log = open("job.log", "w")
#
#         # We don't record job re-runs
#         if not rerun:
#             test_uuid = uuid4()
#             test_case = TestResult(uuid=test_uuid, start=now())
#             test_case.fullname = job["qname"]
#             if "description" in job.keys():
#                 test_case.description = job["description"]
#         else:
#             test_case = None
#
#
# #        pname = job["qname"][0:-(len(job["name"])+1)]
# #        elems = pname.split('.')
#         elems = qname.split('.')
#
#         if len(elems) > 4:
#             # When we more elements in the qualified name than
#             # will fit in the PARENT::SUITE::SUBSUITE scheme.
#             #
#             # We do a bit of middle compression to maximize 
#             # readability. 
#
#             collapse_root = True
#
#             if collapse_root:
#                 # Collapse leaf elements
#
#
#                 root = ""
#                 for i,e in enumerate(elems[:-4]):
#                     if i > 0:
#                         root += "."
#                     root += e
#
# #                print("root=%s suite=%s sub_suite=%s" % (root, elems[-3], elems[-2]))
#                 if test_case is not None:
#                     test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=root))
#                     test_case.labels.append(Label(name=LabelType.SUITE, value=elems[-3]))
#                     test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[-2]))
#                     test_case.name = elems[-1]
#             else:
#                 # Collapse leaf elements
#                 if test_case is not None:
#                     test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=elems[0]))
#                     test_case.labels.append(Label(name=LabelType.SUITE, value=elems[1]))
#                     test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[2]))
#
#                 subsuite = ""
#                 for i,e in enumerate(elems[3:]):
#                     if i > 0:
#                         subsuite += "."
#                     subsuite += e
#                 if test_case is not None:
#                     test_case.name = subsuite
#         else:
#             if test_case is not None:
#                 test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=elems[0]))
#
#                 if len(elems) > 1:
#                     test_case.labels.append(Label(name=LabelType.SUITE, value=elems[1]))
#
#                 if len(elems) > 2:
#                     test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=elems[2]))
#                 test_case.name = job["name"]
#
#
#         if test_case is not None:
#             self.reporter.schedule_test(test_uuid, test_case)
#
#         proc = subprocess.Popen(
#             cmdline,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT)
#
#         while True:
#             line = proc.stdout.readline()
#             if not line:
#                 break
#
#             line = line.decode()
#             line_s = line.strip()
#             if line[0] == '@': # and line.startswith("@step"):
#                 if line.startswith("@step-begin"):
#                     begin = len("@step-begin")
#                     end = -1
#
#                     while begin < len(line) and line[begin].isspace():
#                         begin += 1
#                     end = begin + 1
#                     while end < len(line) and not line[end].isspace():
#                         end += 1
#
#                     key = line[begin:end]
#
#                     if test_case is not None:
#                         if key not in self.step_m.keys():
#                             root = TestStepResult(name=key)
#                             uuid = uuid4()
#                             self.reporter.start_step(None, uuid, root)
#                             self.step_m[key] = [(uuid, root)]
#                         step_s = self.step_m[key]
#
#                         parent_uuid = None if len(step_s) == 0 else step_s[-1][0]
#                         uuid = uuid4()
#
#                         step = TestStepResult(name=line[end+1:])
#                         # Mark failed until we get confirmation of the step ending
#                         step.status = Status.FAILED
#                         step_s.append((uuid, step))
#                         self.reporter.start_step(parent_uuid, uuid, step)
#
#                 elif line.startswith("@step-end"):
#                     begin = len("@step-end")
#                     end = -1
#
#                     while begin < len(line) and line[begin].isspace():
#                         begin += 1
#                     end = begin + 1
#                     while end < len(line) and not line[end].isspace():
#                         end += 1
#
#                     key = line[begin:end]
#
#                     if test_case is not None:
#                         if key not in self.step_m.keys():
#                             self.step_m[key] = []
#                         step_s = self.step_m[key]
#
#                         if len(step_s) == 0:
#                             print("Warning: unmatched step-end")
#                         else:
#                             uuid, step = step_s.pop()
#                             step.status = Status.PASSED
#                             self.reporter.stop_step(uuid, stop=now())
#                 elif line.startswith("@fatal"):
#                     begin = len("@fatal")
#                     end = -1
#
#                     while begin < len(line) and line[begin].isspace():
#                         begin += 1
#                     end = begin + 1
#                     while end < len(line) and not line[end].isspace():
#                         end += 1
#
#                     key = line[begin:end]
#
#                     # Add to the test status itself
#                     if test_case is not None:
#                         if test_case.statusDetails is None:
#                             test_case.statusDetails = StatusDetails(message=line[len("@fatal"):])
#                         else:
#                             test_case.statusDetails.message += "\n" + line[len("@fatal"):]
#             elif line_s.startswith("Exception:"):
#                 # Save the exception
#                 if test_case is not None:
#                     if test_case.statusDetails is None:
#                         test_case.statusDetails = StatusDetails(message=line)
#                     else:
#                         test_case.statusDetails.message += "\n" + line
#
#             job_log.write(line)
#
#         job_log.close()
#
#         # Close out remaining steps
#         for key in self.step_m.keys():
#             for step_i in self.step_m[key]:
# #                step_i[1].status = Status.PASSED
#                 self.reporter.stop_step(step_i[0], stop=now())
#
#         code = proc.wait()
#         if code == 0:
#             if not os.path.isfile("status.txt"):
#                 if test_case is not None:
#                     test_case.status = Status.FAILED
#             else:
#                 with open("status.txt", "r") as fp:
#                     pass_count = 0
#                     fail_count = 0
#                     for line in fp.readlines():
#                         if line.find("PASS") != -1:
#                             pass_count += 1
#                         if line.find("FAIL") != -1:
#                             fail_count += 1
#
#                     if test_case is not None:
#                         if pass_count > 0 and fail_count == 0:
#                             test_case.status = Status.PASSED
#                         else:
#                             test_case.status = Status.FAILED
#         elif code == 124: # Timeout
#             with open("job.log", "a") as fp:
#                 fp.write("MKDV Error: Timeout after %s\n" % (
#                     str(job["limit-time"])))
#         else:
#             if test_case is not None:
#                 test_case.status = Status.FAILED
#
#         # Process the env file to pull out specific result labels
#         env = {}
#         if os.path.isfile("job.env"):
#             with open("job.env", "r") as fp:
#                 for line in fp.readlines():
#                     eq_idx = line.find('=')
#                     pc_idx = line.find('%%')
#
#                     if eq_idx != -1 and (pc_idx == -1 or pc_idx > eq_idx):
#                         key = line[:eq_idx].strip()
#                         value= line[eq_idx+1:].strip()
#                         env[key] = value
#
#         tool = env["MKDV_TOOL"] if "MKDV_TOOL" in env.keys() else "UNKNOWN"
#         if test_case is not None:
#             test_case.labels.append(Label(name=LabelType.FRAMEWORK, value=tool))
#             test_case.labels.append(Label(name=LabelType.HOST, value=socket.gethostname()))
#
#         # Add labels coming through the test description        
#         if "labels" in job.keys() and job["labels"] is not None:
#             for l in job["labels"]:
#                 name = next(iter(l))
#                 val = l[name]
#                 if test_case is not None:
#                     test_case.labels.append(Label(name=name, value=val))
#
#         if "parameters" in job.keys() and job["parameters"] is not None:
#             for p in job["parameters"]:
#                 name = next(iter(p))
#                 val = p[name]
#                 if test_case is not None:
#                     test_case.parameters.append(Parameter(name=name, value=val))
#
#         if "MKDV_JOB_PARAMETERS" in env.keys():
#             params = env["MKDV_JOB_PARAMETERS"]
#
#             i=0
#             while i < len(params):
#                 while i < len(params) and params[i].isspace():
#                     i += 1
#
#                 eq = params.find('=', i)
#
#                 if eq != -1:
#                     end = eq
#                     while end < len(params) and not params[end].isspace():
#                         end += 1
#                     key = params[i:eq]
#                     val = params[eq+1:end]
#
#                     if test_case is not None:
#                         test_case.parameters.append(Parameter(name=key, value=val))
#                     i = end
#                 else:
#                     break
#
#
#         if test_case is not None:
#             self.reporter.attach_file(
#                 uuid4(), 
#                 "job.log",
#                 "log")
#
#
#         if "attachments" in job.keys() and test_case is not None:
#             for a in job["attachments"]:
#                 name = next(iter(a))
#                 path = a[name]
#
#                 self.reporter.attach_file(
#                     uuid4(),
#                     path,
#                     name)
#
#
#         if test_case is not None:
#             test_case.stop=now()
#             self.reporter.close_test(test_uuid)
#

    
