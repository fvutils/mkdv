'''
Created on Nov 23, 2021

@author: mballance
'''
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager

class _ConfigFile(object):
    """Dummy configuration file required by FuseSoC"""
    
    def __init__(self, content, name=""):
        self.name = name
        self.lines = content.splitlines()
        
    def seek(self, where):
        pass
    
    def __iter__(self):
        return iter(self.lines)
    
class CoreManagerW(CoreManager):
    
    def __init__(self):
        cfg_file = _ConfigFile("")
        cfg = Config(file=cfg_file)
        
        super().__init__(cfg)

        