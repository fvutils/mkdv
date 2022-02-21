'''
Created on Nov 7, 2021

@author: mballance
'''
from mkdv.stream_provider import StreamProvider
from _io import StringIO

class StreamProviderTesting(StreamProvider):
    
    def __init__(self, filemap : dict = None):
        super().__init__()
        if filemap is None:
            self.filemap = {}
        else:
            self.filemap = filemap
    
    def open(self, path, mode):
        if path in self.filemap.keys():
            return StringIO(self.filemap[path])
        else:
            return None
        
    def close(self, fp):
        pass
        