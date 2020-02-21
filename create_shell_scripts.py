#!/usr/bin/env python3
import os
import platform
import pandas as pd
import sys

def extract_repo_name(link):
    #https://github.com/mosdef-hub/foyer.git
    return '.'.join((link.split('/')[-1]).split('.')[0:-1:1])

git_links_file = sys.argv[1]
extension = sys.argv[2]
cs_repo_path = sys.argv[3]

#Create .sh file to clone these
clone_script = open(cs_repo_path + '/clone_repos.sh', 'w')
process_script = open('process_repos.sh','w')

with open(git_links_file) as f:
    for link in f:
        link = link.strip()
        clone_script.write('git clone ' + link + '\n')
        process_script.write('python3 reuse_data_collector.py ' + extension + ' ' + cs_repo_path + '/' + extract_repo_name(link) + '\n')

clone_script.close()
process_script.close()

#python3 reuse_data_collector.py py ../cs_repos/galaxy
