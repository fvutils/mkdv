'''
Created on Dec 29, 2020

@author: mballance
'''
import os
import yaml
from mkdv.job_spec import JobSpec
from mkdv.job_spec_set import JobSpecSet
from mkdv.job_spec_gen import JobSpecGen
from mkdv.yaml_loader import YamlLoader
from yaml.loader import FullLoader
from mkdv.stream_provider import StreamProvider
from typing import List, Tuple
import json
import jsonschema
from mkdv.runners.runner_spec import RunnerSpec
from copy import deepcopy
from mkdv.job_vars import JobVars
from mkdv.generator_spec import GeneratorSpec
from mkdv.job_limit_spec import JobLimitSpec
from fusesoc.vlnv import Vlnv
from mkdv.runners.runner_rgy import RunnerRgy
from mkdv.runners.runner import Runner

class JobspecLoader(object):
    
    def __init__(self, 
                 stream_provider : StreamProvider=None,
                 runner = None,
                 core_mgr = None):
        self.prefix_s = []
        self.variables_s = []
        self.dir_s = []
        self.tool_s = []
        self.count_s = [1]
        
        if runner is None:
            runner = RunnerSpec("makefile")
            runner.config["makefile"] = "${MKDV_JOBDIR}/mkdv.mk"
            
        self.core_mgr = core_mgr
        
        self.runner_s = [runner]
        self.setup_vars_dflt_s = [JobVars()]
        self.setup_vars_ovr_s = [JobVars()]
        self.run_vars_dflt_s = [JobVars()]
        self.run_vars_ovr_s = [JobVars()]
        
        self.setup_generators = [{}]
        self.run_generators = [{}]

        self.attachments_s = [set()]
        self.labels_s = [set()]
        self.limit_s = []
        self.parameters_s = [JobVars()]
        
        self.jobspec_s = None
        self.dflt_mkdv_mk = None
        self.ps = ":"
        self.debug = 0

        if stream_provider is None:
            stream_provider = StreamProvider()
            
        self.stream_provider = stream_provider
        self.schema = None
        pass
    
    def load(self, specfile : str):
        self.jobspec_s = JobSpecSet()
        
        if self.debug > 0:
            print("--> JobspecLoader::load specfile=%s" % specfile)

        self.process_yaml(specfile, None)

        if self.debug > 0:
            print("<-- JobspecLoader::load %d jobs %d genjobs" % (
                len(self.jobspec_s.jobspecs), len(self.jobspec_s.jobspec_gen)))
            
        return self.jobspec_s
    
    def load_specs(self, specs : List[str]):
        self.jobspec_s = JobSpecSet()
        
        if self.debug > 0:
            print("--> JobspecLoader::load_specs")

        for specfile in specs:
            self.process_yaml(specfile, None)

        if self.debug > 0:
            print("<-- JobspecLoader::load_specs")
            
        return self.jobspec_s    
    
    def find_tests(self, path, prefix):
        # First, see if there is a mkdv.mk here        
        if os.path.isfile(os.path.join(path, "mkdv.mk")):
            print("TODO: Found test " + prefix)
            pass
        else:
            # Need to go digging
            for p in os.listdir(path):
                if os.path.isdir(p) and p != ".." and p != ".":
                    self.find_tests(os.path.join(path, p), prefix + "." + p)
                    
    def process_yaml(self, path, prefix):
        if self.debug > 0:
            print("--> process_yaml: %s %s" % (str(path), str(prefix)))

        dir = os.path.dirname(path)
        
        if dir == "":
            dir = os.getcwd()

        if self.debug > 0:            
            print("process_yaml: dir=%s" % dir)
        self.dir_s.append(dir)
        data = None
        
        if self.debug > 0:            
            print("path=%s dir=%s" % (path, dir))
        
        fp = self.stream_provider.open(path, "r")
        
        data = yaml.load(fp, Loader=FullLoader)
        
        if self.debug > 0:
            print("File: %s ; Data: %s" % (path, str(data)))
        
        self.stream_provider.close(fp)
        
        if self.schema is None:
            mkdv_dir = os.path.dirname(os.path.abspath(__file__))
            schema_dir = os.path.join(mkdv_dir, "share", "schema")
            with open(os.path.join(schema_dir, "mkdv_schema.json"), "r") as fp:
                self.schema = json.load(fp)

        if self.debug > 0:
            print("--> validate: data=%s schema=%s" % (
                str(data), str(self.schema)))
        try:
            jsonschema.validate(data, self.schema)
        except Exception as e:
            print("Error: validation of %s failed" % path)
            raise e
        
        if self.debug > 0:
            print("<-- validate")
            
        if data is None:
            # Empty file
            # TODO: issue a warning
            print("Warning: job-spec file %s is empty" % path)
            return
        
        for key in data.keys():
            if key == "job":
                self.process_job(data["job"])
            elif key == "job-group":
                self.process_job_group(data["job-group"])
            else:
                raise Exception("Unknown top-level section %s" % key)
            
        self.dir_s.pop()
            
        # if "name" in data.keys():
        #     if prefix is None:
        #         prefix = data["name"]
        #     else:
        #         prefix += "." + data["name"]
        #
        # self.prefix_s.append(prefix)
        # self.dir_s.append(dir)
        # self.process_root(data)
        # self.dir_s.pop()
        # self.prefix_s.pop()
        
        if self.debug > 0:
            print("<-- process_yaml: %s %s" % (str(path), str(prefix)))
            
    def process_job(self, job_s) -> JobSpec:
        if self.debug > 0:
            print("--> process_job %s" % job_s["name"])
            
        js = JobSpec(job_s["name"], self.fullname(job_s["name"]))
        js.basedir = self.dir_s[-1]
        
        if "description" in job_s.keys():
            js.description = job_s["description"]
            
        if "tool" in job_s.keys():
            js.tool = job_s["tool"]
        elif len(self.tool_s) > 0:
            js.tool = self.tool_s[-1]
            
        if "count" in job_s.keys():
            js.count = job_s["count"]
        else:
            js.count = self.count_s[-1]
        
        if self.debug > 0:
            print("Set job count: %d" % js.count)

        if "setup-vars" in job_s.keys():
            dflt, ovr = self.process_vars(
                job_s["setup-vars"],
                self.setup_vars_dflt_s[-1],
                self.setup_vars_ovr_s[-1])
            if self.tool is not None:
                ovr["__tool"] = self.tool
            else:
                ovr["__tool"] = ""
                
            js.setupvars = dflt
        else:
            js.setupvars = self.setup_vars_dflt_s[-1].copy()

        if "run-vars" in job_s.keys():
            if self.debug > 0:
                print("run-vars: name=%s incoming=%s" % (js.name, str(self.run_vars_dflt_s[-1])))
            dflt, ovr = self.process_vars(
                job_s["run-vars"],
                self.run_vars_dflt_s[-1],
                self.run_vars_ovr_s[-1])
            js.runvars = dflt
        else:
            if self.debug > 0:
                print("run-vars: applying default name=%s incoming=%s" % (js.name, str(self.run_vars_dflt_s[-1])))
            js.runvars = self.run_vars_dflt_s[-1].copy()
            
        js.attachments = self.attachments_s[-1].copy()
        if "attachments" in job_s.keys():
            for a in job_s["attachments"]:
                js.attachments.add(a)
            
        js.labels = self.labels_s[-1].copy()
        if "labels" in job_s.keys():
            for label in job_s["labels"]:
                js.labels.add(label)
                
        js.parameters = self.parameters_s[-1].copy()
        if "parameters" in job_s.keys():
            for key,value in job_s["parameters"].items():
                js.parameters[key] = value

        if "runner" in job_s.keys():
            js.runner_spec = self.process_runner(job_s["runner"])
        else:
            # Accept the runner from above. It's required to have a default
            js.runner_spec = deepcopy(self.runner_s[-1])
            pass
        
        
        if "limit" in job_s.keys():
            js.limit = self.process_limit(job_s["limit"])
        elif len(self.limit_s) > 0:
            js.limit = self.limit_s[-1].copy()
            
        
        self.process_job_run_generators(job_s, js)
#        self.process_job_setup_generators(job_s, js)
        
#        self.process_job_setup_vars(job_s, js)
#        self.process_job_run_vars(job_s, js)

        if js.runner_spec is not None and js.runner_spec.auto_discover:
            runner : Runner = RunnerRgy.inst().get_runner(js.runner_spec.runner_id)
            job_specs = runner.query_jobs(js)
            self.jobspec_s.jobspecs.extend(job_specs)
        else:
            self.jobspec_s.jobspecs.append(js)

#        self.process_job

        if self.debug > 0:
            print("<-- process_job")
        return js
    
    def process_job_run_generators(self, job_s, js):
        # First, bring forward run generators from the stack
        
        rg = {}
        
        if "run-generators" in job_s.keys():
            for rg_s in job_s["run-generators"]:
                g_id = rg_s["id"]
                gen_s = GeneratorSpec(g_id)
                if "config" in rg_s.keys():
                    gen_s.config = rg_s["config"].copy()
                
                if g_id in rg.keys():
                    rg[g_id].append(gen_s)
                
        rg = self.run_generators[-1].copy()
        
    def process_runner(self, runner_s):
        config = RunnerSpec(runner_s["id"])
        if "auto-discover" in runner_s.keys():
            config.auto_discover = runner_s["auto-discover"]
        if "config" in runner_s.keys():
            config.config = runner_s["config"].copy()
        return config
    
    def process_limit(self, limit_s):
        if len(self.limit_s) > 0:
            limit = self.limit_s[-1].copy()
        else:
            limit = JobLimitSpec()
            
        if "time" in limit_s.keys():
            limit.time = limit_s["time"]
            
        return limit
    
    def process_job_group(self, job_group_s):
        if self.debug > 0:
            print("--> process_job_group")
            
        if "name" in job_group_s.keys():
            self.prefix_s.append(job_group_s["name"])
            
        if "count" in job_group_s.keys():
            print("Set group count: %d" % job_group_s["count"])
            self.count_s.append(job_group_s["count"])
            
        if "tool" in job_group_s.keys():
            self.tool_s.append(job_group_s["tool"])
            
        if "runner" in job_group_s.keys():
            runner = self.process_runner(job_group_s["runner"])
            self.runner_s.append(runner)
            
        if "limit" in job_group_s.keys():
            limit = self.process_limit(job_group_s["limit"])
            self.limit_s.append(limit)
            
        if "setup-vars" in job_group_s.keys():
            dflt, ovr = self.process_vars(
                job_group_s["setup-vars"],
                self.setup_vars_dflt_s[-1],
                self.setup_vars_ovr_s[-1])
            self.setup_vars_dflt_s.append(dflt)
            self.setup_vars_ovr_s.append(ovr)
            
        if "run-vars" in job_group_s.keys():
            dflt, ovr = self.process_vars(
                job_group_s["run-vars"],
                self.setup_vars_dflt_s[-1],
                self.setup_vars_ovr_s[-1])
            self.run_vars_dflt_s.append(dflt)
            self.run_vars_ovr_s.append(ovr)
            
        if "attachments" in job_group_s.keys():
            attachments = self.attachments_s[-1].copy()
            for a in job_group_s["attachments"]:
                attachments.add(a)
            self.attachments_s.append(attachments)
            
        if "labels" in job_group_s.keys():
            labels = self.labels_s[-1].copy()
            for label in job_group_s["labels"]:
                labels.add(label)
            self.labels_s.append(labels)
            
        if "parameters" in job_group_s.keys():
            parameters = self.parameters_s[-1].copy()
            for key,value in job_group_s["parameters"].items():
                parameters[key] = value
            self.parameters_s.append(parameters)

        if self.debug > 0:            
            print("job_group_s: %s" % str(job_group_s))
            print("  keys: %s" % str(job_group_s.keys()))
            
        for j in job_group_s["jobs"]:
            if self.debug > 0:
                print("j: %s" % str(j))
            if "job-group" in j.keys():
                self.process_job_group(j["job-group"])
            elif "vlnv" in j.keys():
                self.process_vlnv_jobspec_path(j)
            elif "path" in j.keys():
                # TODO: need to pass along context path
                self.process_jobspec_path(j["path"])
            else: # "name" in j.keys():
                self.process_job(j)
            
        if "name" in job_group_s.keys():
            self.prefix_s.pop()
            
        if "count" in job_group_s.keys():
            self.count_s.pop()
            
        if "tool" in job_group_s.keys():
            self.tool_s.pop()
            
        if "runner" in job_group_s.keys():
            self.runner_s.pop()
            
        if "limit" in job_group_s.keys():
            self.limit_s.pop()
            
        if "setup-vars" in job_group_s.keys():
            self.setup_vars_dflt_s.pop()
            self.setup_vars_ovr_s.pop()
            
        if "run-vars" in job_group_s.keys():
            self.run_vars_dflt_s.pop()
            self.run_vars_ovr_s.pop()
            
        if "attachments" in job_group_s.keys():
            self.attachments_s.pop()
            
        if "labels" in job_group_s.keys():
            self.labels_s.pop()
            
        if "parameters" in job_group_s.keys():
            self.parameters_s.pop()
            
        if self.debug > 0:
            print("<-- process_job_group")
            
    def process_vlnv_jobspec_path(self, vlnv_s):
        if self.core_mgr is None:
            raise Exception("No core-manager supplied to handle VLNV %s" % vlnv_s["vlnv"])
        
        flags = { "is_toplevel": True }
        
        if "target" in vlnv_s.keys():
            flags["target"] = vlnv_s["target"]
        
        core = self.core_mgr.get_depends(
            Vlnv(vlnv_s["vlnv"]),
            flags=flags)
        
        for c in core:
            
            c_files = c.get_files(flags)
            
            for f in c_files:
                if f['file_type'] == "testPlanYaml":
                    full_path = os.path.join(c.core_root, f['name'])
                    self.process_jobspec_path(full_path)
            
    
    def process_jobspec_path(self, path):
        if self.debug > 0:
            print("--> process_jobspec_path: %s" % path)
            
        basedir = self.dir_s[-1]
        
        if not os.path.isabs(path):
            path = os.path.join(basedir, path)
            
        dir = os.path.dirname(path)

        if self.debug > 0:
            print("dir=%s" % dir)        
        
        self.dir_s.append(dir)
        data = None
        fp = self.stream_provider.open(path, "r")
        
        data = yaml.load(fp, Loader=FullLoader)
        
        self.stream_provider.close(fp)
        
        if self.schema is None:
            mkdv_dir = os.path.dirname(os.path.abspath(__file__))
            schema_dir = os.path.join(mkdv_dir, "share", "schema")
            with open(os.path.join(schema_dir, "mkdv_schema.json"), "r") as fp:
                self.schema = json.load(fp)

        if self.debug > 0:
            print("--> validate: data=%s schema=%s" % (
                str(data), str(self.schema)))

        try:            
            jsonschema.validate(data, self.schema)
        except Exception as e:
            print("Error: validation failed for %s" % path)
            raise e
            
        
        if self.debug > 0:
            print("<-- validate")
            
        if data is None:
            # Empty file
            # TODO: issue a warning
            print("Warning: job-spec file %s is empty" % path)
            return
        
        for key in data.keys():
            if key == "job":
                self.process_job(data["job"])
            elif key == "job-group":
                self.process_job_group(data["job-group"])
                pass
            else:
                raise Exception("Unknown top-level section %s" % key)        
            
        self.dir_s.pop()
            
        if self.debug > 0:
            print("<-- process_jobspec_path: %s" % path)
        pass
              
    def process_root(self, root):
        self.process_sections(root)
    
    def process_sections(self, section, ignore_keys=None):
        if self.debug > 0:
            print("--> process_sections")
            
        for key in section.keys():
            if self.debug > 0:
                print("section: %s" % key)
            if key == "mkdv.with":
                self.process_with(section[key])
            elif key == "jobs":
                self.process_jobs(section[key])
            else:
                if ignore_keys is None or key not in ignore_keys:
                    raise Exception("Unknown key " + key)
        
        if self.debug > 0:
            print("<-- process_sections")
            
    def process_jobs(self, jobs):
        if self.debug > 0:
            print("--> process_jobs")
        dir = self.dir_s[-1]
        
        for j in jobs:
#            print("j=" + str(j))
            if not isinstance(j, dict):
                raise Exception("Job is not described with a dict: " + str(j))

            testkey = next(iter(j.keys())) 
            
            if self.debug > 0:
                print("testkey: %s" % str(testkey))
                
            prefix = self.prefix_s[-1]
            if self.debug > 0:
                print("prefix: " + str(prefix))
            if prefix is not None:
                testname = prefix + "." + testkey
            else:
                if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                    testname = os.path.basename(dir) + "." + testkey
                else:
                    testname = testkey
            if self.debug > 0:
                print("testname: " + str(testname))
                        
            testdesc = j[testkey]
                
            if testdesc is not None:
                if "path" in testdesc.keys():
                    
                    start_idx = len(self.jobspec_s.jobspecs)
                    
                    if "command" in testdesc.keys():
                        mkdv_mk = self.dflt_mkdv_mk
                        
                        if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                            mkdv_mk = os.path.join(dir, "mkdv.mk")
                            
                        if mkdv_mk is None:
                            raise Exception("No mkdv.mk for generated jobset")
                            
                        # This is a generated jobset
                        spec = JobSpecGen(
                            testname,
                            dir, # srcdir
                            mkdv_mk,
                            testdesc["command"],
                            testdesc["path"])
                        
                        self.jobspec_s.jobspec_gen.append(spec)
                    else:
                        # Path is relative to the current dir
                        testpath = os.path.join(dir, testdesc["path"])
                        if os.path.isfile(testpath):
                            # Pointing to another yaml file
                            self.process_yaml(testpath, testname)
                        elif os.path.isdir(testpath):
                            if os.path.isfile(os.path.join(testpath, "mkdv.yaml")):
#                                print("yaml test")
                                self.process_yaml(os.path.join(testpath, "mkdv.yaml"), testname)
                            elif os.path.isfile(os.path.join(testpath, "mkdv.mk")):
#                                print("Makefile test")
                                self.process_mkdv_mk_test(
                                    os.path.join(testpath, "mkdv.mk"), 
                                    testname,
                                    testkey,
                                    testdesc)
                            else:
                                print("Warning: Test " + testname + " has neither mkdv.mk nor mkdv.yaml")
                        else:
                            print("Warning: Test " + testname + " doesn't point to anything")

                    # The user is customizing settings for these jobs
                    if "run-vars" in testdesc.keys():
                        i = start_idx
                        run_vars = self.read_vars(testdesc["run-vars"])
                        print("Note: Applying test overrides: %s" % str(run_vars))
                        
                        while i < len(self.jobspec_s.jobspecs):
                            j = self.jobspec_s.jobspecs[i]
                            for vk,vv in run_vars.items():
                                j.variables[vk] = vv
                            i += 1
                        
                elif os.path.isfile(os.path.join(dir, "mkdv.mk")):
#                    print("Makefile test with options: " + testname)
                    self.process_mkdv_mk_test(
                        os.path.join(dir, "mkdv.mk"), 
                        testname,
                        testkey,
                        testdesc)
                elif self.dflt_mkdv_mk is not None:
                    self.process_mkdv_mk_test(
                        self.dflt_mkdv_mk,
                        testname,
                        testkey,
                        testdesc)
                else:
                    print("Warning: no idea how to run job %s" % testkey)
            else: # Test with no options
                mkdv_mk = self.dflt_mkdv_mk
                if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                    mkdv_mk = os.path.join(dir, "mkdv.mk")

                if mkdv_mk is None:
                    raise Exception("Test %s has no associated mkdv.mk" % testname)
                
                self.process_mkdv_mk_test(
                    os.path.join(dir, "mkdv.mk"), 
                    testname,
                    testkey,
                    None)
                
        if self.debug > 0:
            print("<-- process_jobs")
            
    def fullname(self, name):
        if len(self.prefix_s) == 0:
            return name
        else:
            return ".".join(self.prefix_s) + "." + name

    def process_with(self, section):
        
        if "variables" not in section.keys():
            raise Exception("mkdv.with requires a variables section")
        
        
            
        var_l = []
        for vs in section["variables"]:
            vk = next(iter(vs))
            if isinstance(vs[vk], (list,tuple)):
                var_l.append((vk, vs[vk]))
            else:
                var_l.append((vk, [vs[vk]]))

        # Sort based on the number of variable values                
        var_l.sort(key=lambda e: len(e[1]))
        
        self.expand_with(var_l, 0, section)
    
    def expand_with(self, var_l, idx, section):
        if len(self.variables_s) > 0:
            vars = self.variables_s.copy()
        else:
            vars = {}
            
        self.variables_s.append(vars)
        for i in range(len(var_l[idx][1])):
            # Set the specific value at this level
            vars[var_l[idx][0]] = var_l[idx][1][i]
            
            if idx+1 < len(var_l):
                # Recurse another level
                self.expand_with(var_l, idx+1, section)
            else:
                # Reached the bottom. Expand the section
                self.process_sections(section, ("variables",))
            
        self.variables_s.pop()
        
    def process_vars(self,
                     var_l : List,
                     var_dflt : dict,
                     var_ovr : dict) -> Tuple[dict,dict]:
        """Processes variable map and produces a tuple of <dflt,ovr>"""
        dflt = JobVars()
        ovr = var_ovr.copy()
        
        # First, process user-specified variables
        for v in var_l:
            if "var" in v.keys():
                # Complex form
                key = v["var"]
                if "override" in v.keys() and v["override"]:
                    override = True
                else:
                    override = False
                
                if "val" in v.keys():
                    # Single value
                    dflt[key] = v["val"]
                elif "append-path" in v.keys():
                    if key in dflt.keys():
                        dflt[key] = dflt[key] + self.ps + v[key]
                    elif key in var_dflt.keys():
                        dflt[key] = var_dflt[key] + self.ps + v[key]
                    else:
                        dflt[key] = v[key]
                elif "prepend-path" in v.keys():
                    if key in dflt.keys():
                        dflt[key] = v[key] + self.ps + dflt[key]
                    elif key in var_dflt.keys():
                        dflt[key] = v[key] + self.ps + var_dflt[key]
                    else:
                        dflt[key] = v[key]
                elif "append-list" in v.keys():
                    if key in dflt.keys():
                        if isinstance(dflt[key], list):
                            dflt[key].append(v[key])
                        else:
                            dflt[key] = [dflt[key], v[key]]
                    else:
                        dflt[key] = v[key]
                elif "prepend-list" in v.keys():
                    if key in dflt.keys():
                        if isinstance(dflt[key], list):
                            dflt[key].insert(0, v[key])
                        else:
                            dflt[key] = [v[key], dflt[key]]
                    else:
                        dflt[key] = v[key]
                        
                if override:
                    ovr[key] = dflt[key]
            else:
                key = next(iter(v.keys()))
                dflt[key] = v[key]
                
            
        
        # Insert default values
        for key in var_dflt.keys():
            if key not in dflt.keys():
                dflt[key] = var_dflt[key]
        
        # Override specified values
        for key in var_ovr.keys():
            dflt[key] = var_ovr[key]
            
            if key not in ovr.keys():
                ovr[key] = var_ovr[key]
            
        return (dflt, ovr)
            
    
    def process_mkdv_mk_test(self, mkdv_mk, fullname, localname, testdesc):
        if self.debug > 0:
            print("--> process_mkdv_mk_test mkdv_mk=%s fullname=%s localname=%s" % (
                mkdv_mk, fullname, localname))
            
        test = JobSpec(mkdv_mk, fullname, localname)
        self.jobspec_s.jobspecs.append(test)

        if testdesc is not None:       
            if "variables" in testdesc.keys():
                if self.debug > 0:
                    print("processing variables")
                variables = testdesc["variables"]
                if isinstance(variables, list):
                    for vs in variables:
                        vk = next(iter(vs))
                        test.variables[vk] = vs[vk]
                else:
                    print("Warning: variables is not a dict: " + str(variables))
                
                if len(self.variables_s) > 0:
                    ov = self.variables_s[-1]
                
                    for vk in ov.keys():
                        test.variables[vk] = ov[vk]
            else:
                if self.debug > 0:
                    print("no variables")
            if "limit-time" in testdesc.keys():
                test.limit_time = testdesc["limit-time"]
        
            if "description" in testdesc.keys():
                test.description = testdesc["description"]
            
            if "labels" in testdesc.keys():
                for l in testdesc["labels"]:
                    name = next(iter(l))
                    value = l[name]
                    test.labels.add_label(name, value)
                    
            if "parameters" in testdesc.keys():
                for p in testdesc["parameters"]:
                    name = next(iter(p))
                    value = p[name]

                    # TODO: format based on Python type?                    
                    test.add_parameter(name, str(value))

            if "attachments" in testdesc.keys():
                for a in testdesc["attachments"]:
                    # Each attachment is a dict of name/path
                    name = next(iter(a))
                    path = a[name]
                
                    test.attachments.append((name, path))
                    
        if self.debug > 0:
            print("<-- process_mkdv_mk_test mkdv_mk=%s fullname=%s localname=%s" % (
                mkdv_mk, fullname, localname))
            
    def read_vars(self, vars) -> dict:
        ret = {}
        if isinstance(vars, list):
            for vs in vars:
                vk = next(iter(vs))
                ret[vk] = vs[vk]
        else:
            print("Warning: variables is not a dict: " + str(variables))        
            
        return ret
        
                
