'''
Created on Nov 19, 2021

@author: mballance
'''
from fusesoc.config import Config
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import Library
from fusesoc.vlnv import Vlnv
from mkdv import get_packages_dir
import os
import logging
import yaml
import sys
import jinja2


class _ConfigFile(object):
    """Dummy configuration file required by FuseSoC"""
    
    def __init__(self, content, name=""):
        self.name = name
        self.lines = content.splitlines()
        
    def seek(self, where):
        pass
    
    def __iter__(self):
        return iter(self.lines)
    
class _TemplateLoader(jinja2.BaseLoader):
    
    def __init__(self, path):
        self.path = path
        
    def get_source(self, environment, template):
        if not os.path.exists(self.path):
            raise jinja2.TemplateNotFound(template)
        mtime = os.path.getmtime(self.path)
        try:
            with open(self.path, "r") as fp:
                source = fp.read()
        except:
            print("Error reading file \"" + self.path + "\"");
        return source, self.path, lambda: mtime == os.path.getmtime(self.path)

def cmd_filespec(args):
    cfg_file = _ConfigFile("")
    cfg = Config(file=cfg_file)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    cm = CoreManager(cfg)
    
    if not hasattr(args, "output") or args.output is None:
        args.output = "-"
    
    packages_dir = get_packages_dir()
    project_dir = os.path.dirname(packages_dir)
    cm.add_library(Library("project", project_dir))

    if args.library_path is not None:
        for lib in args.library_path:
            colon_i = lib.find(':')
            if colon_i > 1:
                path = lib[colon_i+1:]
                lib_name = lib[:colon_i]
            else:
                path = lib
                lib_name = "cmdline"
            
            cm.add_library(Library(lib_name, path))
        
    top_flags = { "is_toplevel": True }
    
    filepath_m = {}
    
    template_m = _find_builtin_templates()
    
    if not hasattr(args,"template") or args.template is None:
        # Report on available templates
        raise Exception("No template specified. Avaiable: %s" % " ".join(list(template_m.keys())))

    if os.path.isfile(args.template):
        template = args.template
    else:
        if args.template not in template_m.keys():
            raise Exception("Template %s not present. Avaiable: %s" % (
                args.template,
                " ".join(list(template_m.keys()))))
        else:
            template = template_m[args.template]
        
    with open(args.filespec, "r") as fp:
        filespec = yaml.load(fp, Loader=yaml.loader.FullLoader)

    if "filespec" not in filespec.keys():
        raise Exception("YAML filespec does not contain 'filespec'")
    
    fs = filespec["filespec"]
    
    for v in fs:
    
        out =  v["out"]
    
        for e in out:
            top_flags = {"is_toplevel": True}
            
            if "flags" in e.keys():
                f = e["flags"]
                    
                if isinstance(f, list):
                    for fi in f:
                        top_flags[fi] = True
                else:
                    top_flags[f] = True
                    
            core_deps = cm.get_depends(Vlnv(v["vlnv"]), flags=top_flags)
                    
            name = e["name"]
    
            flags = {}
            file_type = set()
        
            t = e["type"]
            if isinstance(t, list):
                for ti in t:
                    file_type.add(ti)
            else:
                file_type.add(t)
                
            if "flags" in e.keys():
                f = e["flags"]
                
                if isinstance(f, list):
                    for fi in f:
                        flags[fi] = True
                else:
                    flags[f] = True

            if "include" in e.keys():
                include = e["include"]
            else:
                include = False
                
#                print("file_type: %s ; include=%s" % (str(file_type), str(include)))

            files = _collect_files(core_deps, file_type, flags, include)
            filepath_m[name] = files

    # Now, generate the output
    t_loader = _TemplateLoader(template)
    env = jinja2.Environment(loader=t_loader)
    templ = env.get_template(template)
    out = templ.render({ "files" : filepath_m})
    
    if args.output == "-":
        sys.stdout.write(out)
    else:
        with open(args.output, "w") as fp:
            fp.write(out)

        
def _collect_files(core_deps, file_type, flags, include):
    files = []

    for d in core_deps:
        file_flags = {"is_toplevel": True}
        
#        if hasattr(args, "target") and args.target is not None:
#            file_flags["target"] = args.target
            
        # Bring in flags to specify which content is included
        file_flags.update(flags)
        
        d_files = d.get_files(file_flags)

        for f in d_files:
            if file_type is None or f['file_type'] in file_type:
                is_include = 'include_path' in f.keys() and f['include_path']
                
                if is_include == include:
                    files.append(os.path.join(d.core_root, f['name']))    

    return files    

def _find_builtin_templates():
    mkdv_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(mkdv_dir, "share", "templates")
   
    templates = {} 
    for f in os.listdir(templates_dir):
        if f != "." and f != "..":
            ext = os.path.splitext(f)[1]
            if f.startswith("filespec.") and ext == ".in":
                id = f[len("filespec."):-len(".in")]
                templates[id] = os.path.join(templates_dir, f)
    return templates
                
