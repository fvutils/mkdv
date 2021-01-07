'''
Created on Jan 2, 2021

@author: mballance
'''

class JobQueue(object):
    
    def __init__(self, mkdv_mk):
        self.mkdv_mk = mkdv_mk
        self.build_run = False
        self.build_pass = False
        self.cachedir = None
        self.jobs = []
        
    