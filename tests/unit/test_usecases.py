'''
Created on Nov 6, 2021

@author: mballance
'''
from unittest.case import TestCase
from mkdv_test_case import MkdvTestCase

class TestUsecases(MkdvTestCase):
    
    
    def test_gtest_runner_auto_discover(self):
        text = """
        job-group:
            runner:
                id: googletest
                auto-discover: true
                config:
                    executable: ${BUILD_DIR}/test/test_main
        """
        self.validate(text)
        
    def test_gtest_runner_auto_discover_1(self):
        text = """
        job-group:
            jobs:
                - job:
                  name: abc
        """
        self.validate(text)
        
    def test_gtest_runner_auto_discover_2(self):
        text = """
        job:
            name: abc
        """
        self.validate(text)
        
    def test_generator_basics(self):
        text = """
        job:
            name: abc
            run-generators:
                - id: genfile
                  config:
                      file: config.dat
                      content: |
                        This is content
                          indented slightly
                        Inline
        """
        model = self.validate(text)
        print("model: %s" % str(model))

    def test_gtest_runner_explicit(self):
        text = """
        job-group:
            runner:
                id: googletest
                auto-discover: true
                config:
                    executable: ${BUILD_DIR}/test/test_main
            run-generators:
                - id: foo
                  config:
                    file: foo.bar
            jobs:
                - job:
                  name: testFoo
                  run-vars:
                    - GTEST_FILTER: MyTest.foo
                  run-generators:
                    - id: file-writer
                      config:
                        file: config.dat
                        content: |
                          This is content that goes in the file...
                    
                  
        """
        self.validate(text)
    