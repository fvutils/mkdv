'''
Created on Nov 16, 2021

@author: mballance
'''

_in_main = False
_active_cfg = None

def in_main():
    global _in_main
    _in_main = True
    
def active_cfg():
    global _active_cfg
    return _active_cfg

def setup(cfg):
    from mkdv.__main__ import main
    global _in_main
    global _active_cfg

    _active_cfg = cfg
        
    if not _in_main:
        main()
    pass