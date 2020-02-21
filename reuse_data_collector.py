#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import pandas as pd
import sys

def get_files(extension, path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(extension):
            #if extension in file:
                files.append(os.path.join(r, file))
    return files

extension = sys.argv[1]
path_arg = sys.argv[2]

if (not os.path.exists(path_arg)):
    print("Path not found")

print(get_files(extension, path_arg))
