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
