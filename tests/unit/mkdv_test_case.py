'''
Created on Nov 6, 2021

@author: mballance
'''
from _io import StringIO
import json
import os
from unittest.case import TestCase

import yaml
from yaml.loader import Loader
import jsonschema


class MkdvTestCase(TestCase):
    
    def validate(self, doc):
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        mkdv_dir = os.path.dirname(os.path.dirname(unit_dir))
        schema_dir = os.path.join(mkdv_dir, "src", "mkdv", "share", "schema")
        with open(os.path.join(schema_dir, "mkdv_schema.json"), "r") as fp:
            schema = json.load(fp)        

        text_ds = yaml.load(StringIO(doc), Loader=Loader)
#        print("text_ds: %s" % str(text_ds))
        
        jsonschema.validate(text_ds, schema)
        
        return text_ds