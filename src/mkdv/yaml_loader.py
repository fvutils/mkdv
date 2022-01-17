'''
Created on May 28, 2021

@author: mballance
'''
from yaml.composer import Composer
from yaml.constructor import FullConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from mkdv.mkdv_yaml_composer import MkdvYamlComposer


class YamlLoader(Reader, Scanner, Parser, Composer, FullConstructor, Resolver):
    
    class LineDict(dict):
        pass
    
    class LineInt(int):
        pass
    
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        MkdvYamlComposer.__init__(self)
        FullConstructor.__init__(self)
        Resolver.__init__(self)
        
    def compose_node(self, parent, index):
        # Stash the associated locations on the YAML node
        ret = Composer.compose_node(self, parent, index)
        ret.__lineno__ = self.line
        ret.__linepos__ = self.column
        
        return ret
   
    def construct_object(self, node, deep=False):
        ret = FullConstructor.construct_object(self, node, deep=deep)
        
        if hasattr(node, "__lineno__"):
            ret.lineno = node.__lineno__
            ret.linepos = node.__linepos__
        else:
            ret.lineno = -1
            ret.linepos = -11
        
        return ret
    
         