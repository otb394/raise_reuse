#!/usr/bin/env python3
import os
import platform
import pandas as pd
import sys
import re
import ntpath

ext_to_multiple_ext = {'py': ['py'], 'cpp': ['cpp', 'cxx', 'cc']}
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

def get_directories(path, extensions):
    dirs = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        dirs.append(r)
    return dirs

def get_files(path, extensions):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if any(file.endswith('.' + ext) for ext in extensions):
            #if extension in file:
                files.append(os.path.join(r, file))
    return files

def extract_info(fil, extension):
    #lines of code
    #Extract imports
    lines = 0
    pat = re_map[extension]
    imports = set()
    try:
        with open(fil) as f:
            for line in f:
                lines+=1
                try:
                    if (pat.match(line)):
                        imports.add(line.strip())
                except:
                    print("Encoding error for file = %s" % fil)
    except:
        print("Encoding error for file = %s" % fil)
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
def get_internal_modules(files, directories, extensions):
    ret = []
    if ("py" in extensions):
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

def is_internal_mod_python(statement, internal, source_dir):
    parts = statement.split(".")
    #print('source dir = %s' % source_dir)
    return all(x in internal for x in parts) or (parts[0].lower() == source_dir.lower())

def is_internal_import(imp, extension, internal, source_dir):
    current_mods = extract_modules(imp, extension)
    if (extension == 'py'):
        return all(is_internal_mod_python(c, internal, source_dir) for c in current_mods) 
    else:
        return None

# Returns true, if an import statement is for an external package
def is_external_import(imp, extension, internal, source_dir):
    return not is_internal_import(imp, extension, internal, source_dir)

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
source_dir_name = ntpath.basename(path_arg)
if (len(sys.argv) > 3):
    project_name = sys.argv[3]
else:
    project_name = source_dir_name

#print('path_arg = %s' % path_arg)
#print('source_dir_name = %s' % source_dir_name)
if (not os.path.exists(path_arg)):
    print("Path not found")


extensions = ext_to_multiple_ext[extension]
files = get_files(path_arg, extensions)
dirs = get_directories(path_arg, extensions)

internal_modules = get_internal_modules(files, dirs, extensions)
#print("Internal modules")
#print(internal_modules)

nfiles = 0
n_ext_cs_imp = 0
n_ext_noncs_imp = 0
n_imp = 0
n_loc = 0
n_files_with_external_imps = 0
for f in files:
    nfiles+=1
    ext = f.split('.')[-1]
    if (ext not in extensions):
        print('Extension %s not in extension list' % ext)
        print('File path is %s' % f)
        continue
    lines, imp = extract_info(f, ext)
    n_loc +=lines
    n_imp += len(imp)
    external_imp_flag = False
    for statement in imp:
        if (is_external_import(statement, ext, internal_modules, source_dir_name)):
            if (is_package_CS(statement, ext)):
                print(statement)
                n_ext_cs_imp+=1
            else:
                n_ext_noncs_imp+=1
            external_imp_flag = True
    if (external_imp_flag):
        n_files_with_external_imps += 1

data = [[project_name, nfiles, n_files_with_external_imps, n_ext_cs_imp, n_ext_noncs_imp, n_imp, n_loc]]
df = pd.DataFrame(data, columns=['Project Name', 'Files', 'Files with external imports', 'External CS Imports', 'External Non CS Imports', 'All Imports', 'Lines of code'])
print(df)
df.to_csv(source_dir_name + '.csv', index=False)
