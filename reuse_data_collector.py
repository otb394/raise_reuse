#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import pandas as pd
import sys
import re
import ntpath

ext_to_regex = {'py': '(?m)^(?:from[ ]+(\S+)[ ]+)?import[ ]+(\S+)(?:[ ]+as[ ]+\S+)?[ ]*$'}
re_map = {'py': re.compile(ext_to_regex['py'])}
cs_external_packages = {'py' : ["abaco","yank","signac-flow","forcebalance","openmmtools","foyer","parsl","radical.pilot","apbs-pdb2pqr","MAST","hydroshare","MetPy","luigi","RMG-Py","mdanalysis","yt","pymatgen","galaxy"]}

def get_loc(fil):
    #Improve to remove blank lines and comments
    lines = 0
    with open(fil) as f:
        for line in f:
            lines+=1
    return lines

def get_directories(path, extension):
    dirs = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        dirs.append(r)
    return dirs

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

# Plural because more than one module may be imported in one statement
def get_modules_python(imp):
    modules = []
    if imp[:7] == "import " and ", " not in imp:
        if " as " in imp:
            modules.append(imp[7:imp.find(" as ")])
        else:
            modules.append(imp[7:])
    elif imp[:5] == "from ":
        modules.append(imp[5:imp.find(" import ")])

    elif ", " in imp:
        imp = imp[7:].split(", ")
        modules = modules+imp

    else:
        print(imp)
    return modules

# Returns list of packages/modules in same package
def get_internal_modules(files, directories, extension):
    ret = []
    if (extension == "py"):
        for f in files:
            basename = ntpath.basename(f)
            fileName, fileExt = os.path.splitext(basename)
            ret.append(fileName)
        for d in directories:
            basename = ntpath.basename(d)
            ret.append(basename)
    else:
        return None
    return ret

# Extract package/module names from import
def extract_modules(imp, extension):
    if (extension == "py"):
        return get_modules_python(imp)
    else:
        return None

def is_internal_import(imp, extension, internal):
    current_mods = extract_modules(imp, extension)
    if (extension == 'py'):
        all_curr_mods = set()
        for mod in current_mods:
            all_pack_mods = mod.split(".")
            for pack_mods in all_pack_mods:
                all_curr_mods.add(pack_mods)
        return all(elem in internal for elem in all_curr_mods)
    else:
        return None

# Returns true, if an import statement is for an external package
def is_external_import(imp, extension, internal):
    return not is_internal_import(imp, extension, internal)

# Package assumed to be external
def is_package_CS(imp, extension):
    externals =  cs_external_packages[extension]# Get this list
    externals = [x.lower() for x in externals]
    if (extension == "py"):
        packs = extract_modules(imp, extension)
        packs = [x.split('.')[0] for x in packs]
        return any(elem.lower() in externals for elem in packs)
    else:
        return None

extension = sys.argv[1]
path_arg = sys.argv[2]
project_name = sys.argv[3]

if (not os.path.exists(path_arg)):
    print("Path not found")


files = get_files(path_arg, extension)
dirs = get_directories(path_arg, extension)

internal_modules = get_internal_modules(files, dirs, extension)
print("Internal modules")
print(internal_modules)

nfiles = 0
n_ext_cs_imp = 0
n_ext_noncs_imp = 0
n_imp = 0
n_loc = 0
for f in files:
    nfiles+=1
    lines, imp = extract_info(f, extension)
    n_loc +=lines
    n_imp += len(imp)
    for statement in imp:
        if (is_external_import(statement, extension, internal_modules)):
            if (is_package_CS(statement, extension)):
                print(statement)
                n_ext_cs_imp+=1
            else:
                n_ext_noncs_imp+=1
data = [[project_name, nfiles, n_ext_cs_imp, n_ext_noncs_imp, n_imp, n_loc]]
df = pd.DataFrame(data, columns=['Project Name', 'Files', 'External CS Imports', 'External Non CS Imports', 'All Imports', 'Lines of code'])
print(df)
