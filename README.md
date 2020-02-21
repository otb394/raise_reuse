1. Put the links for the git repos in git\_links.txt
1. Run python3 create\_shell\_scripts.py path/to/git\_links.txt extension path/to/repo/clone/location to create shell scripts to be run.
1. Two files created: clone\_repos.sh at the repo/clone/location and process\_repos.sh at location of running create\_shell\_scripts.py
1. Convert both shell scripts to executable using chmod +x filename.sh
1. Execute clone\_repos.sh
1. Execute process\_repos.sh
1. Run combine\_results.py path/to/result/csv
1. Final result in result.csv
