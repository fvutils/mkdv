'''
Created on May 28, 2021

@author: mballance
'''
from unittest.case import TestCase
import os
import shutil
import yaml
from mkdv.jobspec_loader import JobspecLoader
from typing import Dict
from mkdv.job_spec_gen_loader import JobSpecGenLoader

class MkdvSysTestCase(TestCase):
    
    def setUp(self):
        testdir = os.path.dirname(os.path.abspath(__file__))
        mkdv_dir = os.path.dirname(os.path.dirname(testdir))
        
        rundir = os.path.join(mkdv_dir, "rundir")
        self.testdir = os.path.join(rundir, self.id())

        print("testdir=" + str(self.testdir))        
        if os.path.isdir(self.testdir):
            shutil.rmtree(self.testdir)
        
        os.makedirs(self.testdir)
        
        self.savedir = os.getcwd()
        os.chdir(self.testdir)
        
        TestCase.setUp(self)
        
    def tearDown(self):

#        print("tearDown " + str(self._outcome))
        outcome = self._outcome
        
#        print("errors: " + str(outcome.errors))
        os.chdir(self.savedir)
        
        TestCase.tearDown(self)
        
    def runLoadJobSpec(self, 
                       file_m : Dict[str,str], 
                       exp_s : set(),
                       specfile=None):
        
        for f in file_m.keys():
            f_dir = os.path.dirname(f)
            if f_dir != "" and not os.path.isdir(f_dir):
                os.makedirs(f_dir)
            with open(f, "w") as fp:
                fp.write(file_m[f])

        loader = JobspecLoader()
        jobspec_s = loader.load(
            os.getcwd(), 
            specfile,
            prefix="test")

        for i,gen in enumerate(jobspec_s.jobspec_gen):
            dir = "gen_%d" % i
            
            os.makedirs(dir)
            
            jobset_sg = JobSpecGenLoader(dir).load(gen)
            
            jobspec_s.jobspecs.extend(jobset_sg.jobspecs)

        for j in jobspec_s.jobspecs:
            self.assertIn(j.fullname, exp_s)
            exp_s.remove(j.fullname)

        self.assertEqual(0, len(exp_s))
                
            
        
