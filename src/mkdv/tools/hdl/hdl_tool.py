'''
Created on Nov 16, 2021

@author: mballance
'''
from mkdv.tools.hdl.hdl_tool_config import HdlToolConfig
import os

class HdlTool(object):
    
    def config(self, cfg : HdlToolConfig):
        raise NotImplementedError("config not implemented for %s" % str(type(self)))
    
    def setup(self, cfg : HdlToolConfig):
        raise NotImplementedError("setup not implemented for %s" % str(type(self)))
    
    def run(self, cfg : HdlToolConfig):
        raise NotImplementedError("setup not implemented for %s" % str(type(self)))
    