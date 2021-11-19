'''
Created on Nov 16, 2021

@author: mballance
'''

class ToolRgy(object):
    
    _inst = None
    
    def __init__(self):
        self.tool_m = {}
        
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = ToolRgy()
        return cls._inst
    