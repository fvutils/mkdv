'''
Created on Nov 16, 2021

@author: mballance
'''

class GeneratorSpec(object):
    
    def __init__(self, gen_id):
        self.gen_id = gen_id
        self.config = {}

    def __hash__(self, *args, **kwargs):
        return hash(self.gen_id)
    
    def __eq__(self, other):
        if not isinstance(other, GeneratorSpec):
            return False
        
        return self.gen_id == other.gen_id and self.config == other.config
    
    