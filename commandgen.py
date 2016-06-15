#!/usr/bin/env python

"""
title:          commandgen.py
description:    create commands for apt-get based on patchlist file
author:         Willis Lin
last-modify:    20160615
version:        1.0
"""

import argparse
import os
import subprocess
import sys
import time

def init_argparse():
    """
    Initialize the argparser.

    @retval: ArgumentParser
    """
    parser = argparse.ArgumentParser(prog='PATCHING_TOOL')

    parser.add_argument('-d', '--directory', default=os.getcwd(),
            help='directory to search if not the current')
    parser.add_argument('-p', '--prefix', default='patchlist',
            help='filename pattern to define files to inspect')
    parser.add_argument('-o', '--output', default=False,
            help='write to file of specified filename instead of printing to stdout')

    return parser

def process_file(prefix, path):
    """
    Search through the current directory and generate the print command for each
    file with the given prefix.

    @param prefix: character string to match with filename of files to process
    @param path: directory to search for the patching list files
    @return: dictionary of arrays specifying packages to install
    """
    files = os.listdir(path)
    retval = {}
    for f in files:
        if f.startswith(prefix):
            key = f.rstrip('.txt')
            retval[key] = []
            fopen = open(f)
            for line in fopen:
                retval[key].append(line.split()[0])

    return retval

def print_install_string(key, entry):
    """
    Prints the "apt-get install" line given a dictionary entry key and row of the
    packages to install.

    @param key: file or node associated with the packages
    @param entry: list of strings representing the package names
    @return: string containing the install line
    """
    return "> entry: {}\nsudo apt-get install {}\n".format(key," ".join(entry))

if __name__ == '__main__':
    argparser = init_argparse()
    args = argparser.parse_args()

    install_records = process_file(args.prefix, args.directory)
    if args.output:  # we want to print to a file
        outputfile = open(args.output, 'w')
        for key, entry in install_records.items():
            outputfile.write(print_install_string(key, entry) + "\n")
        outputfile.close()
    else:
        for key, entry in install_records.items():
            print print_install_string(key, entry)
