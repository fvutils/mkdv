'''
Created on Nov 15, 2021

@author: mballance
'''
import os

from mkdv.job_spec import JobSpec
import yaml


class JobYamlWriter(object):
    
    def __init__(self):
        pass
    
    def write(self, s, spec : JobSpec):
        job_s = {}
        
        job_s["basedir"] = spec.basedir
        job_s["is-setup"] = spec.is_setup
        job_s["cachedir"] = spec.cachedir
        job_s["reportdir"] = spec.reportdir
        job_s["name"]      = spec.name
        job_s["fullname"]  = spec.fullname
        job_s["rerun"] = spec.rerun
        job_s["tool"] = spec.tool
        
        job = {"job" : job_s}
        
        yaml.dump(job, s)
        
        
        # if spec.is_setup:
        #     if len(spec.setupvars) > 0:
        #         fp.write("    variables:\n")
        #         for v in spec.setupvars.keys():
        #             fp.write("        %s: \"%s\"\n" % (v, spec.setupvars[v]))
        # else: # Run job
        #     if len(spec.runvars) > 0:
        #         fp.write("    variables:\n")
        #         for v in spec.runvars.keys():
        #             fp.write("        %s: \"%s\"\n" % (v, spec.runvars[v]))
        # if spec.description is not None:
        #     fp.write("    description: |\n")
        #     for line in spec.description.split("\n"):
        #         fp.write("        %s\n" % line)
        #
        # if len(spec.labels) > 0:
        #     fp.write("    labels:\n")
        #     for key in spec.labels.keys():
        #         fp.write("        - %s: %s\n" % (key, spec.labels[key]))
        #
        # if len(spec.parameters) > 0:
        #     fp.write("    parameters:\n")
        #     for key in spec.parameters.keys():
        #         fp.write("        - %s: %s\n" % (key, spec.parameters[key]))
        #
        # if len(spec.attachments) > 0:
        #     fp.write("    attachments:\n")
        #     for a in spec.attachments:
        #         fp.write("    - %s: %s\n" % (a[0], a[1]))
    