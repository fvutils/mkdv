'''
Created on Apr 13, 2022

@author: mballance
'''

from collections.abc import Mapping

def get_parsed_context(args: list):
    print("get_parsed_context: %s" % str(args))
    
    ret = {}
    
    for a in args:
        if a.find('=') != -1:
            i = a.find('=')
            key = a[:i]
            val = a[i+1:]
            
            ret[key] = val
            
    return ret
            
