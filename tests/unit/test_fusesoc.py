'''
Created on Nov 17, 2021

@author: mballance
'''
from unittest.case import TestCase
import os
from librarymanager import LibraryManager
from fusesoc.config import Config
from coremanager import CoreManager
from fusesoc.librarymanager import Library
from vlnv import Vlnv
from core import Core
import logging

class TestFuseSoc(TestCase):
    
    class ConfigFile(object):
        
        def __init__(self, content, name=""):
            self.name = name
            self.lines = content.splitlines()
            
        def seek(self, where):
            pass
        
        def __iter__(self):
            return iter(self.lines)
    
    def test_smoke(self):
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(unit_dir, "data", "fusesoc", "data1")
        
#        logging.basicConfig(level=logging.DEBUG)
        
        cfg_file = TestFuseSoc.ConfigFile(
            content="""
            """)

        cfg = Config(file=cfg_file)
        
        cm = CoreManager(cfg)
        lib = Library("packages", data_dir)
        cm.add_library(lib)
        
        print("Cores: %s" % str(cm.get_cores()))
        data1 : Core = cm.get_core(Vlnv('data1::core1'))
        print("Core: %s" % data1.core_root)
        print("Filesets: %s" % str(data1.filesets.keys()))
        print("Targets: %s" % str(data1.targets.keys()))
        
        depends = cm.get_depends(Vlnv('data1::core13'), {
#            "is_toplevel": True,
            "target": "pss"
            })
        print("depends: %s" % str(depends))
        print("--> get_files")
        files = depends[0].get_files({
            "is_toplevel": True,
            "target": "pss"})
        print("<-- get_files")
        print("files[pss]: %s" % str(files))
        
        pss_files = []
        for dep in depends:
            files = dep.get_files({
                "is_toplevel": True,
                "target": "pss"
            })
            for f in files:
                if f['file_type'] == 'pssSource':
                    pss_files.append(os.path.join(dep.core_root, f['name']))
        print("pss_files: %s" % str(pss_files))
        
        
        
        