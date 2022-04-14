'''
Created on Apr 13, 2022

@author: mballance
'''

from collections.abc import Mapping

def get_parsed_context(args: list[str] | None) -> Mapping | None:
    print("get_parsed_context: %s" % str(args))