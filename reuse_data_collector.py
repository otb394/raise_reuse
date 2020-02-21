#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import pandas as pd
import sys
import re
import ntpath
import compiler
from compiler.ast import Discard, Const
from compiler.visitor import ASTVisitor

def pyfiles(startPath, extension):
    r = []
    d = os.path.abspath(startPath)
    if os.path.exists(d) and os.path.isdir(d):
        for root, dirs, files in os.walk(d):
            for f in files:
                n, ext = os.path.splitext(f)
                if (ext == ('.'+extension)):
                    r.append([root, f])
    return r

class ImportVisitor(object):
    def __init__(self):
        self.modules = []
        self.recent = []
    def visitImport(self, node):
        self.accept_imports()
        self.recent.extend((x[0], None, x[1] or x[0], node.lineno, 0)
                           for x in node.names)
    def visitFrom(self, node):
        self.accept_imports()
        modname = node.modname
        if modname == '__future__':
            return # Ignore these.
        for name, as_ in node.names:
            if name == '*':
                # We really don't know...
                mod = (modname, None, None, node.lineno, node.level)
            else:
                mod = (modname, name, as_ or name, node.lineno, node.level)
            self.recent.append(mod)
    def default(self, node):
        pragma = None
        if self.recent:
            if isinstance(node, Discard):
                children = node.getChildren()
                if len(children) == 1 and isinstance(children[0], Const):
                    const_node = children[0]
                    pragma = const_node.value
        self.accept_imports(pragma)
    def accept_imports(self, pragma=None):
        self.modules.extend((m, r, l, n, lvl, pragma)
                            for (m, r, l, n, lvl) in self.recent)
        self.recent = []
    def finalize(self):
        self.accept_imports()
        return self.modules

class ImportWalker(ASTVisitor):
    def __init__(self, visitor):
        ASTVisitor.__init__(self)
        self._visitor = visitor
    def default(self, node, *args):
        self._visitor.default(node)
        ASTVisitor.default(self, node, *args) 

def parse_python_source(fn):
    contents = open(fn, 'rU').read()
    ast = compiler.parse(contents)
    vis = ImportVisitor() 

    compiler.walk(ast, vis, ImportWalker(vis))
    return vis.finalize()

ext_to_regex = {'py': '(?m)^(?:from[ ]+(\S+)[ ]+)?import[ ]+(\S+)(?:[ ]+as[ ]+\S+)?[ ]*$'}
re_map = {'py': re.compile(ext_to_regex['py'])}

def get_loc(fil):
    #Improve to remove blank lines and comments
    lines = 0
    with open(fil) as f:
        for line in f:
            lines+=1
    return lines

def get_files(path, extension):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(extension):
            #if extension in file:
                files.append(os.path.join(r, file))
    return files

def extract_info(fil, extension):
    #lines of code
    #Extract imports
    lines = 0
    pat = re_map[extension]
    imports = set()
    with open(fil) as f:
        for line in f:
            lines+=1
            if (pat.match(line)):
                imports.add(line.strip())
    return lines, list(imports)

# Returns list of modules in same package
def get_internal_modules(files, extension):
    ret = []
    if (extension == "py"):
        for f in files:
            basename = ntpath.basename(f)
            fileName, fileExt = os.path.splitext(basename)
            ret.append(fileName)
    else:
        return None
    return ret

# Extract package name from import
def extract_module(imp, extension):
    if (extension == "py"):
        #some
        return None
    else:
        return None

# Returns true, if an import statement is for an external package
def is_external(imp, extension):
    return None


extension = sys.argv[1]
path_arg = sys.argv[2]

if (not os.path.exists(path_arg)):
    print("Path not found")

files = get_files(path_arg, extension)
internal_modules = get_internal_modules(files, extension)
print("Internal modules")
print(internal_modules)

data = []
for f in files:
    lines, imp = extract_info(f, extension)
    data.append([f, lines, imp, len(imp)])

df = pd.DataFrame(data, columns=['Files path', 'LOC', 'Imports','No. of imports'])
print(df)

for f in files:
    print(parse_python_source(f))
