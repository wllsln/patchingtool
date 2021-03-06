## Introduction
patchingtool.py is a simple python tool that gathers package lists from remote
systems on the network and can also compare them in an expected format.

commandgen.py prints the patching list as a single row to allow for easy
copy-paste on apt-get install.

## patchingtool.py

### Dependencies
1. [Python 2.7.10](https://www.python.org/downloads/release/python-2710/) or
   higher - `apt-get install python`
2. [paramiko](http://www.paramiko.org/) - `pip install paramiko`

### Usage 
Get help information:
```bash
python patchingtool.py -h
python patchingtool.py pull -h
python patchingtool.py compare --help
```
Pull a package list from a remote machine:
```bash
python patchingtool.py pull REMOTE_MACHINE_NAME
```
Pull a package list from a remote machine and compare to a local patching list:
```bash
python patchingtool.py compare REMOTE_MACHINE_NAME LOCAL_PATCHING_LIST
```
Compare a local package list and a local patching list:
```bash
python patchingtool.py compare -l LOCAL_PACKAGE_LIST LOCAL_PATCHING_LIST
```
Specify the diff tool in a compare:
```bash
python patchingtool.py compare -d DIFF_TOOL REMOTE_MACHINE_NAME LOCAL_PATCHING_LIST
```

Some caveats:
* Current supported OS flavors are Debian and CentOS.
* <remote-machine-name> can be either the hostname as defined in hosts or an IP
  address.
* A package list is the printout of all installed packages on a system.
* A patching list is the user-defined list of packages in the format:
    * one line per package name
    * each line is PACKAGE_NAME, followed by 4 spaces, followed by
      PACKAGE_VERSION

### Suggestions for improvement
* pull the patching list from bugzilla by providing a bz ticket number
    * use the requests package
    * see if bugzilla has an API
* create configuration to specify valid diff tools

## commandgen.py

### Usage

Get help information:
```bash
python commandgen.py -h
```
Print out the command listing patch lists for the current directory:
```bash
python commandgen.py -p PREFIX
```
Send results to a file:
```bash
python commandgen.py -o OUTPUT_FILE
```
Inspect patchlists from a different directory (path):
```bash
python commandgen.py -d DIRECTORY_PATH
```

### Suggestions for improvement
* allow pattern matching instead of prefix for filenames
