#****************************************************************************
#* hdl_tool_vcs.py
#*
#* Copyright 2022 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import os
import subprocess
import sys
from .hdl_tool import HdlTool
from .hdl_tool_mgr import HdlToolMgr
from .hdl_tool_config import HdlToolConfig

class HdlToolVcs(HdlTool):

    def config(self, cfg : HdlToolConfig):
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_HDL_CLOCKGEN")
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_HDL_VIRTUAL_INTERFACE")
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_BIND")
        

    def setup(self, cfg : HdlToolConfig):
        vlog_options = []

        for inc in cfg.var_l(HdlToolConfig.VL_INCDIRS):
            vlog_options.append("+incdir+%s" % inc)
            
        for d in cfg.var_l(HdlToolConfig.VL_DEFINES):
            vlog_options.append("+define+%s" % d)
            
        for f in cfg.var_l(HdlToolConfig.VL_SRCS):
            print("File: %s" % f)
            vlog_options.append(f)
        
        if not os.path.isdir(cfg.cachedir):
            os.makedirs(cfg.cachedir)

        # Create a work library
        cmd = ['vlib', 'work']
        res = subprocess.run(
            cmd,
            cwd=cfg.cachedir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Process exit with code %d" % res.returncode)

        cmd = ['vlog', '-sv']
        cmd.extend(vlog_options)
        print("cmd=%s" % str(cmd))
        res = subprocess.run(
            cmd,
            cwd=cfg.cachedir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Process exit with code %d" % res.returncode)

    def run(self, cfg : HdlToolConfig):
        vsim_options = []
        
        if not os.path.isdir(cfg.rundir):
            os.makedirs(cfg.rundir)
            
        cmd = ['vmap', 'work', os.path.join(cfg.cachedir, 'work')]
        
        res = subprocess.run(
            cmd,
            cwd=cfg.rundir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Run failed")

        cmd = ['vsim', '-c', '-do', 'run -a; quit -f']        
        for vpi in cfg.var_l(HdlToolConfig.VPI_LIBS):
            vsim_options.extend(["-pli", vpi])
            
        for dpi in cfg.var_l(HdlToolConfig.DPI_LIBS):
            vsim_options.extend(["-sv_lib", os.path.splitext(dpi)[0]])
            
        if cfg.var_b(HdlToolConfig.DEBUG):
            vsim_options.append("-qwavedb=+report=class+signal+memory")
            
        if cfg.var_b(HdlToolConfig.VALGRIND):
            vsim_options.extend(["-valgrind", "--tool=memcheck"])
            
        for arg in cfg.var_l(HdlToolConfig.RUN_ARGS):
            vsim_options.append(arg)
            
        top = cfg.var_l(HdlToolConfig.TOP_MODULE)
        
        if len(top) == 0:
            raise Exception("No top module specified")
        
        vsim_options.extend(top)
        
        cmd.extend(vsim_options)
        
        res = subprocess.run(
            cmd,
            cwd=cfg.rundir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Run failed")
        
        
            
        pass

    def __init__(self):
        pass


HdlToolMgr.inst().register_tool("vcs", HdlToolVcs)