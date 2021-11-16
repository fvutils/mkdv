'''
Created on Nov 9, 2021

@author: mballance
'''
from unittest.case import TestCase
from stream_provider_testing import StreamProviderTesting
from mkdv.jobspec_loader import JobspecLoader
from mkdv.job_spec_set import JobSpecSet
from mkdv.job_queue_builder import JobQueueBuilder

class TestJobqueueBuilder(TestCase):
    
    def test_same_runner_same_settings(self):
        text = """
        job-group:
            name: top
            jobs:
                - name: j1
                  setup-vars:
                    - var1: val1
                - name: j2
                  setup-vars:
                    - var1: val1
                - name: j3
                  setup-vars:
                    - var1: val1
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })
        
        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        
        self.assertEqual(len(specs.jobspecs), 3)
        queue_s = JobQueueBuilder().build(specs.jobspecs)
        self.assertEqual(len(queue_s.queues), 1)
        self.assertEqual(len(queue_s.queues[0].jobs), 4)
        
    def test_same_runner_all_diff_settings(self):
        text = """
        job-group:
            name: top
            jobs:
                - name: j1
                  setup-vars:
                    - var1: val1
                - name: j2
                  setup-vars:
                    - var1: val2
                - name: j3
                  setup-vars:
                    - var1: val3
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })
        
        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        
        self.assertEqual(len(specs.jobspecs), 3)
        queue_s = JobQueueBuilder().build(specs.jobspecs)
        self.assertEqual(len(queue_s.queues), 3)
        for i in range(len(queue_s.queues)):
            self.assertEqual(len(queue_s.queues[i].jobs), 2)

    def test_same_runner_two_diff_settings(self):
        text = """
        job-group:
            name: top
            jobs:
                - name: j1
                  setup-vars:
                    - var1: val1
                - name: j2
                  setup-vars:
                    - var1: val2
                - name: j3
                  setup-vars:
                    - var1: val2
        """
        
        sp = StreamProviderTesting({
            "job.yaml" : text
        })
        
        loader = JobspecLoader(sp)
        loader.tool_s.append("default")
        specs : JobSpecSet = loader.load("job.yaml")
        
        self.assertEqual(len(specs.jobspecs), 3)
        queue_s = JobQueueBuilder().build(specs.jobspecs)
        self.assertEqual(len(queue_s.queues), 2)
        self.assertEqual(len(queue_s.queues[0].jobs), 2)
        self.assertEqual(len(queue_s.queues[1].jobs), 3)


        