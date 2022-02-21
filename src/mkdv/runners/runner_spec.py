'''
Created on Nov 6, 2021

@author: mballance
'''

class RunnerSpec(object):
    
    def __init__(self, runner_id):
        self.runner_id = runner_id
        self.tool_id   = None
        self.auto_discover = False
        self.config = {}
        
    def __hash__(self):
        ret = hash(self.runner_id)
        for k in self.config.keys():
            ret += hash(k)
        return ret
    
    def __eq__(self, other):
        if not isinstance(other, RunnerSpec):
            return False

        return self.runner_id == other.runner_id and self.config == other.config
    
    @staticmethod
    def mkMakeRunnerSpec(mkfile_path : str):
        spec = RunnerSpec("mkdv_mk")
        spec.config["mkfile_path"] = mkfile_path
        return spec
        
    