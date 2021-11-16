'''
Created on Nov 15, 2021

@author: mballance
'''
import os

from mkdv.job_spec import JobSpec


class JobYamlWriter(object):
    
    def __init__(self):
        pass
    
    def write(self,
              job_yaml,
              cachedir,
              spec : JobSpec):
        with open(job_yaml, "w") as fp:
            fp.write("job:\n");
            fp.write("    mkfile: %s\n" % spec.mkdv_mk)
            if spec.is_setup:
                fp.write("    is-setup: True\n")
            else:
                fp.write("    is-setup: False\n")
            fp.write("    cachedir: %s\n" % cachedir)
            fp.write("    reportdir: %s\n" % os.path.join(self.root, "report"))
            fp.write("    name: %s\n" % spec.localname)
            fp.write("    qname: %s\n" % spec.fullname)
            if spec.limit_time is not None:
                fp.write("    limit-time: %s\n" % str(spec.limit_time))
            elif self.limit_time is not None:
                fp.write("    limit-time: %s\n" % str(self.limit_time))
            if spec.rerun:
                fp.write("    rerun: true\n")
            else:
                fp.write("    rerun: false\n")
            if len(spec.variables) > 0:
                fp.write("    variables:\n")
                for v in spec.variables.keys():
                    fp.write("        %s: \"%s\"\n" % (v, spec.variables[v]))
            if spec.description is not None:
                fp.write("    description: |\n")
                for line in spec.description.split("\n"):
                    fp.write("        %s\n" % line)

            if len(spec.labels) > 0:
                fp.write("    labels:\n")
                for key in spec.labels.keys():
                    fp.write("        - %s: %s\n" % (key, spec.labels[key]))
                    
            if len(spec.parameters) > 0:
                fp.write("    parameters:\n")
                for key in spec.parameters.keys():
                    fp.write("        - %s: %s\n" % (key, spec.parameters[key]))

            if len(spec.attachments) > 0:
                fp.write("    attachments:\n")
                for a in spec.attachments:
                    fp.write("    - %s: %s\n" % (a[0], a[1]))
    