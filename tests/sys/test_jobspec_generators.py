'''
Created on May 28, 2021

@author: mballance
'''
from mkdv_sys_test_case import MkdvSysTestCase

class TestJobspecGenerators(MkdvSysTestCase):
    
    def test_smoke(self):
        self.runLoadJobSpec({
            "mkdv.yaml" : """
            jobs:
                - a:
                    path: subdir/mkdv.yaml
            """,
            "subdir/mkdv.yaml" : """
            jobs:
                - b:
                - c:
            """,
            "subdir/mkdv.mk": ""},
            exp_s=[
                "test.a.b",
                "test.a.c"
                ])

    def test_gen_smoke(self):
        self.runLoadJobSpec({
            "mkdv.yaml" : """
            jobs:
                - a:
                    path: mkdv.yaml
                    command: |
                      echo "jobs:" >> mkdv.yaml
                      echo "  - b:" >> mkdv.yaml
                      echo "  - c:" >> mkdv.yaml
            """,
            "mkdv.mk" : ""
            },
            exp_s=[
                "test.a.b",
                "test.a.c"
                ])
        
    def test_gen_variables(self):
        self.runLoadJobSpec({
            "mkdv.yaml" : """
            jobs:
                - a:
                    path: mkdv.yaml
                    command: |
                      echo "jobs:" >> mkdv.yaml
                      echo "  - b:" >> mkdv.yaml
                      echo "    variables:" >> mkdv.yaml
                      echo "      SW_IMAGE=foo.elf" >> mkdv.yaml
                      echo "  - c:" >> mkdv.yaml
                      echo "    variables:" >> mkdv.yaml
                      echo "      SW_IMAGE=bar.elf" >> mkdv.yaml
            """,
            "mkdv.mk" : ""
            },
            exp_s=[
                "test.a.b",
                "test.a.c"
                ])        
                
    def test_smoke2(self):
        pass