'''
Created on Nov 6, 2021

@author: mballance
'''
from mkdv_test_case import MkdvTestCase
from mkdv.jobspec_loader import JobspecLoader
from stream_provider_testing import StreamProviderTesting
from mkdv.job_spec_set import JobSpecSet

class TestSpecLoader(MkdvTestCase):

    def test_load_single_job(self):
        text = """
        job:
          name: abc
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 1)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[0].fullname, "abc")
            
    def test_load_single_job_group(self):
        text = """
        job-group:
          name: abc
          labels: 
            - def
            - def
          jobs:
            - name: abc
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 1)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[0].fullname, "abc.abc")

    def test_load_single_job_group_cascading_tool(self):
        text = """
        job-group:
          name: abc
          tool: tool1
          labels: 
            - def
            - def
          jobs:
            - name: abc
            
            - name: def
              tool: tool2
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 2)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[0].fullname, "abc.abc")
        self.assertEqual(specs.jobspecs[0].tool, "tool1")
        self.assertEqual(specs.jobspecs[1].name, "def")
        self.assertEqual(specs.jobspecs[1].fullname, "abc.def")
        self.assertEqual(specs.jobspecs[1].tool, "tool2")
        
    def test_load_single_job_group_two_jobs(self):
        text = """
        job-group:
          name: abc
          labels: 
            - def
            - def
          jobs:
            - name: abc
            - name: def
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 2)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[1].name, "def")
        self.assertEqual(specs.jobspecs[0].fullname, "abc.abc")
        self.assertEqual(specs.jobspecs[1].fullname, "abc.def")

    def test_load_single_job_group_two_files(self):
        file1 = """
        job-group:
          name: abc
          labels: 
            - def
            - def
          jobs:
            - path: file2.yaml
        """
        
        file2 = """
        job-group:
            jobs:
              - name: abc
              - name: def
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : file1,
            "file2.yaml" : file2
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 2)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[1].name, "def")
        self.assertEqual(specs.jobspecs[0].fullname, "abc.abc")
        self.assertEqual(specs.jobspecs[1].fullname, "abc.def")

    def test_load_single_job_setup_generator(self):
        file1 = """
        job:
          name: abc
          setup-generators:
            - id: abc
              config:
                a: b
                c: d
          runner:
            id: makefile
            config:
              path: ${basedir}/Makefile
              properties:
                - a
                - b
              
        """
        
        file2 = """
        job-group:
            jobs:
              - job:
                  name: abc
              - job:
                  name: def
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : file1,
            "file2.yaml" : file2
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 1)
        self.assertEqual(specs.jobspecs[0].name, "abc")
        self.assertEqual(specs.jobspecs[0].fullname, "abc")

    def test_dflt_var_simple(self):
        file1 = """
        job-group:
            setup-vars:
              - var1: val1
              
            jobs:
              - name: j1
              - name: j2
                setup-vars:
                  - var1: val2
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : file1
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 2)
        self.assertEqual(specs.jobspecs[0].name, "j1")
        self.assertEqual(specs.jobspecs[0].fullname, "j1")
        self.assertEqual(specs.jobspecs[1].name, "j2")
        self.assertEqual(specs.jobspecs[1].fullname, "j2")
        self.assertEqual(specs.jobspecs[0].setupvars["var1"], "val1")
        self.assertEqual(specs.jobspecs[1].setupvars["var1"], "val2")

    def test_dflt_var_complex(self):
        file1 = """
        job-group:
            setup-vars:
              - var: var1
                val: val1
              
            jobs:
              - name: j1
              - name: j2
                setup-vars:
                  - var: var1
                    val: val2
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : file1
        })

        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        self.assertEqual(len(specs.jobspecs), 2)
        self.assertEqual(specs.jobspecs[0].name, "j1")
        self.assertEqual(specs.jobspecs[0].fullname, "j1")
        self.assertEqual(specs.jobspecs[1].name, "j2")
        self.assertEqual(specs.jobspecs[1].fullname, "j2")
        self.assertEqual(specs.jobspecs[0].setupvars["var1"], "val1")
        self.assertEqual(specs.jobspecs[1].setupvars["var1"], "val2")


