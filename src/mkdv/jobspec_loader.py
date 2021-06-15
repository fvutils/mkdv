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

class JobspecLoader(object):
    
    def __init__(self):
        self.prefix_s = []
        self.variables_s = []
        self.dir_s = []
        
        self.jobspec_s = None
        self.dflt_mkdv_mk = None
        self.debug = 1
        pass
    
    def load(self, 
             root, 
             specfile=None,
             dflt_mkdv_mk=None,
             prefix=None):
        self.jobspec_s = JobSpecSet()
        self.dflt_mkdv_mk = dflt_mkdv_mk
        
        if self.debug > 0:
            print("--> JobspecLoader::load specfile=" + str(specfile))
        
#        if prefix is not None:
#            self.prefix_s.append(prefix)
            
        if specfile is not None:
            self.process_yaml(specfile, prefix)
        elif os.path.isfile(os.path.join(root, "mkdv.yaml")):
            # This test suite is described by YAML files
            self.process_yaml(os.path.join(root, "mkdv.yaml"), prefix)
            pass
        else:
            # This test suite is described by individual mkfiles
            self.find_tests(root, None)

#        if prefix is not None:            
#            self.prefix_s.pop()
            
#        for t in self.test_l:
#            print("Test: " + t.fullname + " " + t.mkdv_mk + " " + str(t.variables))

        if self.debug > 0:
            print("<-- JobspecLoader::load %d jobs %d genjobs" % (
                len(self.jobspec_s.jobspecs), len(self.jobspec_s.jobspec_gen)))
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
        data = None
        with open(path) as f:
            data = yaml.load(f, Loader=FullLoader)
            
        if data is None:
            # Empty file
            # TODO: issue a warning
            print("Warning: job-spec file %s is empty" % path)
            return
            
        if "name" in data.keys():
            if prefix is None:
                prefix = data["name"]
            else:
                prefix += "." + data["name"]
                
        self.prefix_s.append(prefix)
        self.dir_s.append(dir)
        self.process_root(data)
        self.dir_s.pop()
        self.prefix_s.pop()
              
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
            print("prefix: " + str(prefix))
            if prefix is not None:
                testname = prefix + "." + testkey
            else:
                if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                    testname = os.path.basename(dir) + "." + testkey
                else:
                    testname = testkey
            print("testname: " + str(testname))
                        
            testdesc = j[testkey]
                
            if testdesc is not None:
                if "path" in testdesc.keys():
                    
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
            
    
    def process_mkdv_mk_test(self, mkdv_mk, fullname, localname, testdesc):
        test = JobSpec(mkdv_mk, fullname, localname)
        self.jobspec_s.jobspecs.append(test)
        
        if testdesc is not None and "variables" in testdesc.keys():
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
                
                