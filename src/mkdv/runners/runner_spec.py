'''
Created on Nov 6, 2021

@author: mballance
'''

class RunnerSpec(object):
    
    def __init__(self, runner_id, tool_id):
        self.runner_id = runner_id
        self.tool_id   = tool_id
        self.config = {}
        # Setup vars are an important part of determining uniqueness
        self.setup_vars = {}
        # 
        self.run_vars = {}
        
    def __hash__(self):
        return hash(self.runner_id) + hash(self.config)
    
    def __eq__(self, other):
        if not isinstance(other, RunnerSpec):
            return False

        return self.runner_id == other.runner_id and self.config == other.config
    
    @staticmethod
    def mkMakeRunnerSpec(mkfile_path : str):
        spec = RunnerSpec("mkdv_mk")
        spec.config["mkfile_path"] = mkfile_path
        return spec
        
    