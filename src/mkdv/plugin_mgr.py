'''
Created on Apr 14, 2022

@author: mballance
'''
import importlib
import os
import pkgutil


class PluginMgr(object):
    
    _inst = None
    
    def __init__(self):
        self.loaded_paths = set()

        dir = os.path.dirname(os.path.abspath(__file__))
                
        self.load_plugins("mkdv.tools.hdl")
        
    def load_plugins(self, path):
        if path in self.loaded_paths:
            return
       
        print("path=%s" % path) 
        self.loaded_paths.add(path)
        
        importlib.import_module(path)
        
    
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = PluginMgr()
        return cls._inst
    