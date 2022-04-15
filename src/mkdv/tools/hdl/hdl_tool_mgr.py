'''
Created on Apr 14, 2022

@author: mballance
'''
from mkdv.plugin_mgr import PluginMgr

class HdlToolMgr(object):

    _inst = None
    
    def __init__(self):
        self.hdl_tool_m = {}
        
        # Ensure plugins are loaded
        pm = PluginMgr.inst()
        pass
    
    def register_tool(self, name, cls):
        self.hdl_tool_m[name] = cls
        
    def setup(self, cfg):
        if cfg.tool not in self.hdl_tool_m.keys():
            raise Exception("Tool %s is not supported" % cfg.tool)
        
        tool = self.hdl_tool_m[cfg.tool]()
        
        tool.setup(cfg)
        
    def run(self, cfg):
        if cfg.tool not in self.hdl_tool_m.keys():
            raise Exception("Tool %s is not supported" % cfg.tool)
        
        tool = self.hdl_tool_m[cfg.tool]()
        
        tool.run(cfg)

    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = HdlToolMgr()
        return cls._inst
        