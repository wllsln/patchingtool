#!/usr/bin/env python

"""
title:          patchingcompare.py
description:    tool to help compare package list to patching list
author:         Willis Lin
last-modify:    20160401
version:        1.0
"""

import argparse
import getpass
import os
import paramiko
import subprocess
import sys
import time

def init_argparse():
    """
    Initialize the argparser.

    @retval: ArgumentParser
    """
    parser = argparse.ArgumentParser(prog='PATCHING_TOOL')
    subparsers = parser.add_subparsers(dest='command')

    # create the parser for the "pull" command
    parser_pull = subparsers.add_parser('pull', help='pull a package list')
    parser_pull.add_argument('machine', help='hostname or IP to query')

    # create the parser for the "compare" command
    parser_compare = subparsers.add_parser('compare', help='compare two lists')
    parser_compare.add_argument('machine', help='hostname or IP to query')
    parser_compare.add_argument('patch_file', help='local patching list file')
    parser_compare.add_argument('-d','--diff-tool', nargs=1,
            choices=['colordiff','diff','meld','wdiff'],
            help='specify a diff tool to use in compare')
    parser_compare.add_argument('-l', '--local', action='store_true',
            help='use a local package file instead of querying a machine')
    return parser

def parse_exec_cmd(paramiko_output):
    """
    Pull console output from stdout of paramiko .exec_command.

    @param paramiko_output: result from running .exec_command
    @retval: string representing single line of console return
    """
    stdin, stdout, stderr = paramiko_output
    readout = stdout.readlines().pop()
    return readout.rstrip()

def get_package_list(remote_machine, for_compare):
    """
    Access remote machine to generate a dpkg list. Pull the package list to the
    local machine.

    @param remote_machine: machine name or IP address to get dpkg list
    @param for_compare: True will pull specially-formated package list,
        else will pull the typical list
    @return: file name of dpkg list .txt
    """
    # set up remote connection
    user = raw_input("Username for {}: ".format(remote_machine))
    passwd = getpass.getpass("Password for {} user {}: ".format(remote_machine, user))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(remote_machine, username=user, password=passwd)

    # pull info from remote machine
    version_check = "cat /etc/issue.net"
    stdin, stdout, stderr = client.exec_command(version_check)
    version = stdout.readlines().pop()  # check for alternative distro
    date = parse_exec_cmd(client.exec_command("date +'%Y%m%d_%H%M%S'"))  # get remote time
    hostname = parse_exec_cmd(client.exec_command("hostname"))  # get remote hostname

    # dpkg_query based on linux distribution
    dpkg_query = "dpkg-query -W -f='${Package}    ${Version}\n'"  # default=debian
    if version.find("CentOS") > 0:
        hostname = hostname.split(".")[0]  # CentOS hostname includes subdomain
        dpkg_query = "rpm -qa --qf '%{NAME}    %{VERSION}-%{RELEASE}\n' | sort"

    # switch enabled to just copy over the regular dpkg list
    if not for_compare:
        if version.find("CentOS") > 0:
            dpkg_query = "rpm -qa"
        else:
            dpkg_query = "dpkg -l"

    # generate the dpkg list
    output_file_name = "_".join([date,hostname,"dpkg"]) + ".txt"
    if not for_compare:
        output_file_name = "_".join([date.split("_")[0],hostname,
            "package","list"]) + ".txt"
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
    print "Package list pulled: " + output_file_name
    return output_file_name

def compare_with_tool(difftool, pkg_list, patch_list):
    """
    Compare the package list to the patching list with the specified difftool.

    @param difftool: name of the difftool to call
    @param pkg_list: name of machine package list
    @param patch_list: name of the patching list
    @return: none, opens the meld process
    """
    subprocess.Popen([difftool, pkg_list, patch_list])

def show_difference(pkg_list, patch_list):
    """
    Print to screen only where patching list entries differ from package list entries.

    @param pkg_list: name of machine package list
    @param patch_list: name of patching list
    @return: none
    """
    EQUAL, NEQUAL, MISSING = 1, -1, 0
    pkg_file = open(pkg_list)
    patch_file = open(patch_list)
    delimiter = "    "

    # helper function to print to console with formatting
    def print_helper(compare, package, pversion, dversion):
        if compare == EQUAL: prefix = " "
        elif compare == NEQUAL: prefix = "d"  # d for different
        else:
            prefix = "m"  # m for missing
            dversion = ""
        print "{} {} - {} - {}".format(prefix, package, pversion, dversion)

    # helper function to parse entries from dpkg
    def parse_dpkg_row(dpkg_row):
        [pkg, ver] = dpkg_row.rstrip().split(delimiter)
        return pkg, ver

    # compare the two files, print the matches
    # it is assumed the patching list is alpha order
    dpkg, dver = parse_dpkg_row(pkg_file.readline())
    for row in patch_file:
        [ppkg, pver] = parse_dpkg_row(row)
        try:
            while ppkg > dpkg:
                dpkg, dver = parse_dpkg_row(pkg_file.readline())
            if ppkg == dpkg:
                if pver == dver: mode = EQUAL
                else: mode = NEQUAL
            else:  # this package is not in dpkg
                mode = MISSING
                pass
        except StopIteration:  # no more dpkg
            mode = MISSING
        print_helper(mode, ppkg, pver, dver)

    patch_file.close()
    pkg_file.close()

if __name__ == '__main__':
    argparser = init_argparse()
    args = argparser.parse_args()

    if args.command == 'pull':
        get_package_list(args.machine, False)
    elif args.command == 'compare':
        pkg_name = args.machine
        if not args.local:
            pkg_name = get_package_list(args.machine, True)
        if args.diff_tool:
            compare_with_tool(args.diff_tool[0], pkg_name, args.patch_file)
        else:
            show_difference(pkg_name, args.patch_file)

