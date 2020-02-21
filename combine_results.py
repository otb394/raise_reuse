#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import pandas as pd
import sys

def get_files(path, extension):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(extension):
            #if extension in file:
                files.append(os.path.join(r, file))
    return files

results_path = sys.argv[1]
files = get_files(results_path, '.csv')

dfs = [pd.read_csv(f) for f in files]
result_df = pd.concat(dfs, axis=0)
result_df = result_df[result_df['All Imports'] != 0]
print(result_df)
result_df.to_csv('result.csv', index=False)
