# patchingtool

## Usage
```bash
python patchingcompare.py <remote-machine-name> <bz-patching-list>
```

## Dependencies
1. Python 2.7.10
2. paramiko (`pip install paramiko`)

## Suggestions for improvement
* use argparse to setup usage information
* pull the patching list from bugzilla by providing a bz ticket number
    * use the requests package
    * see if bugzilla has an API
* support other diff tool besides meld
* option to specify dpkg_list instead of pulling from remote machine
