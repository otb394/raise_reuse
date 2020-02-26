#!/usr/bin/env python3
import os
import platform
import pandas as pd
import sys
import re
import ntpath

ext_to_multiple_ext = {'py': ['py'], 'cpp': ['cpp', 'cxx', 'cc'], 'c':['c']}
ext_to_header_ext = {'c':['h'], 'py': [], 'cpp': ['h', 'hpp']}
ext_to_regex = {'py': '(?m)^(?:from[ ]+(\S+)[ ]+)?import[ ]+(\S+)(?:[ ]+as[ ]+\S+)?[ ]*$',
                'cpp': '^\s*#\s*include\s*(?P<inclusion><(?P<brackets>\S+?)>|\"(?P<quotes>\S+?)\")',
                'cc': '^\s*#\s*include\s*(?P<inclusion><(?P<brackets>\S+?)>|\"(?P<quotes>\S+?)\")',
                'cxx': '^\s*#\s*include\s*(?P<inclusion><(?P<brackets>\S+?)>|\"(?P<quotes>\S+?)\")',
                'c': '^\s*#\s*include\s*(?P<inclusion><(?P<brackets>\S+?)>|\"(?P<quotes>\S+?)\")'}
re_map = {'py': re.compile(ext_to_regex['py'])}
cs_external_packages = {'py' : ["abaco","yank","signac-flow","forcebalance","openmmtools","foyer","parsl","radical.pilot","apbs-pdb2pqr","MAST","hydroshare","MetPy","luigi","RMG-Py","mdanalysis","yt","pymatgen","galaxy"], 
        'cpp': ["pcmsolver","TauDEM","cpptraj","mpqc","GooFit","SCIRun","changa","cyclus","plumed2","madness","hoomd-blue","irods","openmm","lammps","psi4","dealii","Trilinos"],
        'cc': ["pcmsolver","TauDEM","cpptraj","mpqc","GooFit","SCIRun","changa","cyclus","plumed2","madness","hoomd-blue","irods","openmm","lammps","psi4","dealii","Trilinos"],
        'c': ["pcmsolver","TauDEM","cpptraj","mpqc","GooFit","SCIRun","changa","cyclus","plumed2","madness","hoomd-blue","irods","openmm","lammps","psi4","dealii","Trilinos"],
        'cxx': ["pcmsolver","TauDEM","cpptraj","mpqc","GooFit","SCIRun","changa","cyclus","plumed2","madness","hoomd-blue","irods","openmm","lammps","psi4","dealii","Trilinos"]}

# TODO: We might get better performance if we stick with the map re_map on top
def get_re(extension):
    return re.compile(ext_to_regex[extension])
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
    if (len(extensions) == 0):
        return []
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if any(file.endswith('.' + ext) for ext in extensions):
            #if extension in file:
                files.append(os.path.join(r, file))
    return files

def extract_info(fil, extension, encoding='utf-8'):
    #lines of code
    #Extract imports
    lines = 0
    pat = get_re(extension)
    imports = set()
    try:
        with open(fil, encoding=encoding) as f:
            for line in f:
                lines+=1
                try:
                    if (pat.match(line)):
                        imports.add(line.strip())
                except Exception as e:
                    print("Encoding error for file = %s" % fil)
                    print(e)
                    if (encoding == 'utf-8'):
                        return extract_info(fil, extension, encoding='ISO-8859-1')
    except Exception as e:
        print("Encoding error for file = %s" % fil)
        print(e)
        if (encoding == 'utf-8'):
            return extract_info(fil, extension, encoding='ISO-8859-1')
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
    file_mods = []
    dir_mods = []
    #ret = []
    if (any(["py" in extensions, "cpp" in extensions, "c" in extensions])):
        for f in files:
            basename = ntpath.basename(f)
            fileName, fileExt = os.path.splitext(basename)
            file_mods.append(fileName)
            #ret.append(fileName)
        for d in directories:
            basename = ntpath.basename(d)
            dir_mods.append(basename)
            #ret.append(basename)
    else:
        return None
    return file_mods, dir_mods
    #return ret

# Extract package/module names from import
def extract_modules(imp, extension):
    if (extension == "py"):
        return get_modules_python(imp)
    elif (extension == "cpp" or extension == "cxx" or extension == "cc" or extension == "c"):
        pat = get_re(extension)
        match = pat.search(imp)
        return match.group("inclusion")
        #return imp
    else:
        return None

def is_internal_mod_python(statement, internal, source_dir):
    parts = statement.split(".")
    #print('source dir = %s' % source_dir)
    return all(x in internal for x in parts) or (parts[0].lower() == source_dir.lower())

def is_internal_import(imp, extension, int_files, int_dirs, source_dir):
    internal = int_files + int_dirs
    if (extension == 'py'):
        current_mods = extract_modules(imp, extension)
        return all(is_internal_mod_python(c, internal, source_dir) for c in current_mods) 
    elif (extension in ext_to_multiple_ext['cpp'] or (extension in ext_to_multiple_ext['c'])):
        pat = get_re(extension)
        match = pat.search(imp)
        #print("match = %s" % match)
        #print("imp = %s" % imp) 
        if (match.group("brackets")):
        #if (imp[0] == '<'):
            mod = match.group("brackets")
#            mod = imp[1:-1]
            parts = mod.split('/')
            #return (parts[0].lower() == source_dir.lower())
            parts = [x for x in parts if x != '..' and x != '.']
            return (all(x.split('.')[0] in internal for x in parts) and (('.' not in parts[-1]) \
                    or (parts[-1].split('.')[0] in int_files))) or (parts[0].lower() == source_dir.lower())
        elif (match.group("quotes")):
            mod = match.group("quotes")
#            mod = imp[1:-1]
            parts = mod.split('/')
            parts = [x for x in parts if x != '..' and x != '.']
            return (all(x.split('.')[0] in internal for x in parts) and (('.' not in parts[-1]) \
                    or (parts[-1].split('.')[0] in int_files))) or (parts[0].lower() == source_dir.lower())
            #return all(x.split('.')[0] in internal for x in parts) or (parts[0].lower() == source_dir.lower())
        else:
            print('Unrecognized include')
            sys.exit(1)
    else:
        return None

# Returns true, if an import statement is for an external package
def is_external_import(imp, extension, int_files, int_dirs, source_dir):
    return not is_internal_import(imp, extension, int_files, int_dirs, source_dir)

# Package assumed to be external
def is_package_CS(imp, extension):
    externals =  cs_external_packages[extension]# Get this list
    externals = [x.lower() for x in externals]
    if (extension == "py"):
        packs = extract_modules(imp, extension)
        packs = [x.split('.')[0] for x in packs]
        return any(elem.lower() in externals for elem in packs)
    elif (extension in ext_to_multiple_ext['cpp'] or (extension in ext_to_multiple_ext['c'])):
        pattern = get_re(extension)
        match = pattern.search(imp)
        mod = match.group("brackets") if (match.group("brackets")) else match.group("quotes")
        #mod = imp[1:-1]
        parts = mod.split('/')
        return (parts[0].lower() in externals)
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
#header_extensions = ext_to_header_ext[extension]
#headers = get_files(path_arg, header_extensions)
#headers = []

internal_file_modules, internal_dir_modules = get_internal_modules(files, dirs, extensions)
#internal_modules = get_internal_modules(files, dirs, extensions)
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
        if (is_external_import(statement, ext, internal_file_modules, internal_dir_modules, source_dir_name)):
            if (is_package_CS(statement, ext)):
                #print("INTERNAL")
                print(statement)
                n_ext_cs_imp+=1
            else:
                n_ext_noncs_imp+=1
                #print(statement)
            external_imp_flag = True
        #else:
            #print(statement)
    if (external_imp_flag):
        n_files_with_external_imps += 1

data = [[project_name, nfiles, n_files_with_external_imps, n_ext_cs_imp, n_ext_noncs_imp, n_imp, n_loc]]
df = pd.DataFrame(data, columns=['Project Name', 'Files', 'Files with external imports', 'External CS Imports', 'External Non CS Imports', 'All Imports', 'Lines of code'])
print(df)
df.to_csv(source_dir_name + '.csv', index=False)
