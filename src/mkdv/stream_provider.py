'''
Created on Nov 7, 2021

@author: mballance
'''
import os

class StreamProvider(object):
    
    def open(self, path, mode):
        return open(path, mode)
    
    def close(self, fp):
        fp.close()
    
    def isfile(self, path):
        return os.path.isfile(path)
    
    def isdir(self, path):
        return os.path.isdir(path)
        
    