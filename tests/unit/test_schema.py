'''
Created on Nov 5, 2021

@author: mballance
'''
import json
import os
from unittest.case import TestCase
import yaml
from _io import StringIO
from yaml.loader import Loader
import jsonschema


class TestSchema(TestCase):
    
    def test_valid_schema(self):
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        mkdv_dir = os.path.dirname(os.path.dirname(unit_dir))
        schema_dir = os.path.join(mkdv_dir, "src", "mkdv", "share", "schema")
        with open(os.path.join(schema_dir, "mkdv_schema.json"), "r") as fp:
            schema = json.load(fp)
            
        print("schema: %s" % str(schema))
            
        text = """
        jobs: 
          - job:
              name: abc 
              run-vars:
                - SW_IMAGE: foo.elf
                - var: A
                  val: B
          - job:
              name: def 
          - job-group:
              name: abc
              job:
                - job:
                  name: foo
        """
        
        text_ds = yaml.load(StringIO(text), Loader=Loader)
        print("text_ds: %s" % str(text_ds))
        
        jsonschema.validate(text_ds, schema)
            

    def test_job_group_1(self):
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        mkdv_dir = os.path.dirname(os.path.dirname(unit_dir))
        schema_dir = os.path.join(mkdv_dir, "src", "mkdv", "share", "schema")
        with open(os.path.join(schema_dir, "mkdv_schema.json"), "r") as fp:
            schema = json.load(fp)
            
        print("schema: %s" % str(schema))
            
        text = """
        jobs: 
          - job:
              name: abc 
              run-vars:
                - SW_IMAGE: foo.elf
                - var: A
                  val: B
          - job:
              name: def 
          - job-group:
              name: abc
              jobs:
                - job:
                  name: foo
                - job:
                  name: foo
          - job-group:
              name: abc
              jobs:
                path: /foo/bar
        """
        
        text_ds = yaml.load(StringIO(text), Loader=Loader)
        print("text_ds: %s" % str(text_ds))
        
        jsonschema.validate(text_ds, schema)        
