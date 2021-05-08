'''
Created on Dec 29, 2020

@author: mballance
'''
import os
import yaml
from mkdv.test_spec import TestSpec

class TestLoader(object):
    
    def __init__(self):
        self.test_l = []
        self.prefix_s = []
        self.variables_s = []
        self.dir_s = []
        pass
    
    def load(self, root, specfile=None):
        if specfile is not None:
            self.process_yaml(specfile, None)
        elif os.path.isfile(os.path.join(root, "mkdv.yaml")):
            # This test suite is described by YAML files
            self.process_yaml(os.path.join(root, "mkdv.yaml"), None)
            pass
        else:
            # This test suite is described by individual mkfiles
            self.find_tests(root, None)
            
#        for t in self.test_l:
#            print("Test: " + t.fullname + " " + t.mkdv_mk + " " + str(t.variables))
            
        return self.test_l
    
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
        dir = os.path.dirname(path)
        data = None
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            
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
        for key in section.keys():
            if key == "mkdv.with":
                self.process_with(section[key])
            elif key == "jobs":
                self.process_jobs(section[key])
            else:
                if ignore_keys is None or key not in ignore_keys:
                    raise Exception("Unknown key " + key)
        
            
    def process_jobs(self, jobs):
        dir = self.dir_s[-1]
        
        for j in jobs:
            print("j=" + str(j))
            if not isinstance(j, dict):
                raise Exception("Job is not described with a dict: " + str(j))

            testkey = next(iter(j.keys())) 
                
            prefix = self.prefix_s[-1]            
            if prefix is not None:
                testname = prefix + "." + testkey
            else:
                if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                    testname = os.path.basename(dir) + "." + testkey
                else:
                    testname = testkey
                        
            testdesc = j[testkey]
                
            if testdesc is not None:
                if "path" in testdesc.keys():
                    # Path is relative to the current dir
                    testpath = os.path.join(dir, testdesc["path"])

                    if os.path.isfile(testpath):
                        # Pointing to another yaml file
                        self.process_yaml(testpath, testname)
                    elif os.path.isdir(testpath):
                        if os.path.isfile(os.path.join(testpath, "mkdv.yaml")):
#                            print("yaml test")
                            self.process_yaml(os.path.join(testpath, "mkdv.yaml"), testname)
                        elif os.path.isfile(os.path.join(testpath, "mkdv.mk")):
#                            print("Makefile test")
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
            else: # Test with no options
                if os.path.isfile(os.path.join(dir, "mkdv.mk")):
#                    print("Makefile test without options: " + testname)
                    self.process_mkdv_mk_test(
                        os.path.join(dir, "mkdv.mk"), 
                        testname,
                        testkey,
                        None)
                else:
                    print("Warning: Test " + testname + " is missing mkdv.mk")        

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
        test = TestSpec(mkdv_mk, fullname, localname)
        self.test_l.append(test)
        
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
                
                