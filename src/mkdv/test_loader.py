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
        pass
    
    def load(self, root):
        if os.path.isfile(os.path.join(root, "mkdv.yaml")):
            # This test suite is described by YAML files
            self.process_yaml(os.path.join(root, "mkdv.yaml"), None)
            pass
        else:
            # This test suite is described by individual mkfiles
            self.find_tests(root, None)
            
        for t in self.test_l:
            print("Test: " + t.fullname + " " + t.mkdv_mk + " " + str(t.variables))
            
        return self.test_l
    
    def find_tests(self, path, prefix):
        # First, see if there is a mkdv.mk here        
        if os.path.isfile(os.path.join(path, "mkdv.mk")):
            print("Found test " + prefix)
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
            
        print(data)
            
        if "name" in data.keys():
            if prefix is None:
                prefix = data["name"]
            else:
                prefix += "." + data["name"]
              
        if "tests" in data.keys():
            print("Have tests")
         
            for t in data["tests"]:
                if not isinstance(t, dict):
                    raise Exception("Test is not described with a dict: " + str(t))

                print(t)
                testkey = next(iter(t.keys())) 
                if prefix is not None:
                    testname = prefix + "." + testkey
                else:
                    if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                        testname = os.path.basename(dir) + "." + testkey
                    else:
                        testname = testkey
                        
                testdesc = t[testkey]
                
                if testdesc is not None:
                    if "path" in testdesc.keys():
                        # Path is relative to the current dir
                        testpath = os.path.join(dir, testdesc["path"])

                        if os.path.isfile(testpath):
                            # Pointing to another yaml file
                            self.process_yaml(testpath, testname)
                        elif os.path.isdir(testpath):
                            if os.path.isfile(os.path.join(testpath, "mkdv.yaml")):
                                print("yaml test")
                                self.process_yaml(os.path.join(testpath, "mkdv.yaml"), testname)
                            elif os.path.isfile(os.path.join(testpath, "mkdv.mk")):
                                print("Makefile test")
                                self.process_mkdv_mk_test(
                                    os.path.join(dir, "mkdv.mk"), 
                                    testname,
                                    testkey,
                                    testdesc)
                            else:
                                print("Warning: Test " + testname + " has neither mkdv.mk nor mkdv.yaml")
                        else:
                            print("Warning: Test " + testname + " doesn't point to anything")
                    elif os.path.isfile(os.path.join(dir, "mkdv.mk")):
                        print("Makefile test with options: " + testname)
                        self.process_mkdv_mk_test(
                            os.path.join(dir, "mkdv.mk"), 
                            testname,
                            testkey,
                            testdesc)
                else: # Test with no options
                    if os.path.isfile(os.path.join(dir, "mkdv.mk")):
                        print("Makefile test without options: " + testname)
                        self.process_mkdv_mk_test(
                            os.path.join(dir, "mkdv.mk"), 
                            testname,
                            testkey,
                            None)
                    else:
                        print("Warning: Test " + testname + " is missing mkdv.mk")
        else:
            print("Don't have tests")

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
        
                