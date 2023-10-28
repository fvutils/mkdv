#****************************************************************************
#* hdl_tool_xsim.py
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
import shutil
import subprocess
import sys
from .hdl_tool import HdlTool
from .hdl_tool_mgr import HdlToolMgr
from .hdl_tool_config import HdlToolConfig

class HdlToolXsim(HdlTool):

    def config(self, cfg : HdlToolConfig):
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_HDL_CLOCKGEN")
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_HDL_VIRTUAL_INTERFACE")
        cfg.preppend(HdlToolConfig.VL_DEFINES, "HAVE_BIND")

    def setup(self, cfg : HdlToolConfig):
        vlog_options = []

        vlog_options.append("-L")
        vlog_options.append("uvm")

        for inc in cfg.var_l(HdlToolConfig.VL_INCDIRS):
            vlog_options.append("-i")
            vlog_options.append(inc)
            
        for d in cfg.var_l(HdlToolConfig.VL_DEFINES):
            vlog_options.append("-d")
            vlog_options.append(d)
            
        for f in cfg.var_l(HdlToolConfig.VL_SRCS):
            print("File: %s" % f)
            vlog_options.append(f)
        
        if not os.path.isdir(cfg.cachedir):
            os.makedirs(cfg.cachedir)

        cmd = ['xvlog', '-sv']
        cmd.extend(vlog_options)
        print("cmd=%s" % str(cmd))
        res = subprocess.run(
            cmd,
            cwd=cfg.cachedir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Process exit with code %d" % res.returncode)

        top = cfg.var_l(HdlToolConfig.TOP_MODULE)

        print("top: %s" % str(top))
        
        if len(top) == 0:
            raise Exception("No top module specified")
#        elif len(top) > 1:
#            raise Exception("Too many top modules specified")

        cmd = ['xelab', '-relax', '-s', 'top.snap', '-timescale', '1ns/1ps']
        cmd.extend(top)
        for dpi in cfg.var_l(HdlToolConfig.DPI_LIBS):
            cmd.extend(["-sv_lib", os.path.splitext(dpi)[0]])

#        cmd.extend(vlog_options)
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
            
        cmd = [
            "xsim", 
            "--xsimdir", os.path.join(cfg.cachedir, "xsim.dir"), 
            "--runall"
            ]
        for vpi in cfg.var_l(HdlToolConfig.VPI_LIBS):
            raise NotImplementedError("PLI library %s" % vpi)
#            vsim_options.extend(["-pli", vpi])

        if cfg.var_b(HdlToolConfig.DEBUG):
            raise NotImplementedError("Debug")
#            vsim_options.append("-qwavedb=+report=class+signal+memory")

        if cfg.var_b(HdlToolConfig.VALGRIND):
            raise NotImplementedError("Valgrind")
#            vsim_options.extend(["-valgrind", "--tool=memcheck"])

        for arg in cfg.var_l(HdlToolConfig.RUN_ARGS):
            if arg[0] == '+':
                vsim_options.append("--testplusarg")
                # XSIM doesn't want to actually see the plus in plusarg
                vsim_options.append(arg[1:])
            else:
                raise Exception("Non-plusarg simulation argument \"%s\" is not supported" % arg)
            
        top = cfg.var_l(HdlToolConfig.TOP_MODULE)
        
        if len(top) == 0:
            raise Exception("No top module specified")
        
        vsim_options.append('top.snap')
        vsim_options.append("--ignore_coverage")
        
        cmd.extend(vsim_options)

        print("COMMAND: %s" % str(cmd))

        if os.path.exists(os.path.join(cfg.rundir, "xsim.dir")):
            os.remove(os.path.join(cfg.rundir, "xsim.dir"))

        os.symlink(
            os.path.join(cfg.cachedir, "xsim.dir"),
            os.path.join(cfg.rundir, "xsim.dir")
        )
        
        res = subprocess.run(
            cmd,
            cwd=cfg.rundir,
            stdout=sys.stdout,
            stderr=sys.stderr)
        
        if res.returncode != 0:
            raise Exception("Run failed")
        
HdlToolMgr.inst().register_tool("xsm", HdlToolXsim)

