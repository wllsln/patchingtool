#!/usr/bin/env python

"""
title:          patchingcompare.py
description:    tool to help compare packing list to patching list
author:         Willis Lin
last-modify:    20160125
version:        0.1
usage:          python patchingcompare.py <remote-machine-name> <bz-patching-list>
python-ver:     2.7.10
status:         development
"""

import getpass
import os
import paramiko
import subprocess
import sys
import time

try:
    REMOTE_MACHINE = sys.argv[1]
    PATCHING_LIST = sys.argv[2]
except IndexError:
    print "Usage:  patchingcompare.py <remote-machine-name> <bz-patching-list>"
    sys.exit(1)

def parse_exec_cmd(paramiko_output):
    """
    Pull console output from stdout of paramiko .exec_command

    @param paramiko_output: result from running .exec_command
    @retval: string representing single line of console return
    """
    stdin, stdout, stderr = paramiko_output
    readout = stdout.readlines().pop()
    return readout.rstrip()

def do_dpkg(remote_machine):
    """
    Access remote machine to generate a dpkg list. Pull the package list to the
    local machine.

    @param remote_machine: machine name or IP address to get dpkg list
    @return: file name of dpkg list .txt
    """
    # set up remote connection
    user = 'root'
    passwd = getpass.getpass("Password for {} user {}: ".format(remote_machine, user))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(remote_machine, username=user, password=passwd)

    # determine pkglist name
    date = parse_exec_cmd(client.exec_command("date +'%Y%m%d_%H%M%S'"))  # get remote time
    hostname = parse_exec_cmd(client.exec_command("hostname"))  # get remote hostname
    output_file_name = "_".join([date,hostname,"dpkg"]) + ".txt"

    # generate the dpkg list
    dpkg_query = "dpkg-query -W -f='${binary:Package}    ${Version}\n'"
    query = " ".join([dpkg_query,">",output_file_name])
    stdin, stdout, stderr = client.exec_command(query)
    time.sleep(2)  # allow dpkg to run

    # copy the file to local
    sftp = client.open_sftp()
    sftp.get(output_file_name, output_file_name)
    delete = client.exec_command("rm {}".format(output_file_name))  # remove file

    # close the connection
    sftp.close()
    client.close()
    return output_file_name

def compare_meld(dpkg_list_name, patching_list_name):
    """Compare the dpkg list to the patching list with meld"""
    subprocess.Popen(["meld", dpkg_list_name, patching_list_name])

if __name__ == '__main__':
    dpkg_list = do_dpkg(REMOTE_MACHINE)
    print "Package list copied: " + dpkg_list
    compare_meld(dpkg_list, PATCHING_LIST)

