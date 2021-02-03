#!/usr/bin/env python

import argparse
import re

def matches(string, datastr, index):
    substr = datastr[index:index+len(string)]
    return substr.lower() == string.lower()

def open_slice(slice, prefixes):
    outfile = open("{}{:03d}.ttl".format(args.basename, slice), 'w')
    for prefix in prefixes:
        print(prefix, file=outfile)
    print("", file=outfile)
    return outfile

parser = argparse.ArgumentParser(description="Split a Turtle file into slices")
parser.add_argument("-c", "--chars", type=int, help="approximate number of characters per slice", default=10000000)
parser.add_argument("input", type=str, help="input file name")
parser.add_argument("basename", type=str, help="output file base name")
args = parser.parse_args()

with open(args.input) as infile:
    data = infile.read()

prefixes = []
idx = 0

# prefix extraction
while idx < len(data):
    if matches('@prefix', data, idx):
        start = idx
        idx += len('@prefix')
        while data[idx] != '\n':
            idx += 1
        prefixes.append(data[start:idx])
    elif data[idx] == '#':
        while data[idx] != '\n':
            idx += 1
    elif data[idx] in ('\n', '\t', ' '):
        pass
    else:
        break
    idx += 1

slice = 1
last_split = idx

outfile = open_slice(slice, prefixes)
    
# actual data
while idx < len(data):
    if matches('\n\n', data, idx):
        
        if (idx - last_split) >= args.chars:
            print("", file=outfile)
            outfile.close()
            last_split = idx
            slice += 1
            outfile = open_slice(slice, prefixes)
        else:
            print("\n", file=outfile)
        idx += len("\n\n")
    elif matches('"""', data, idx):
        start = idx
        idx += len('"""')
        while not matches('"""', data, idx):
            idx += 1
        idx += len('"""')
        print(data[start:idx], end='', file=outfile)
    else:
        print(data[idx], end='', file=outfile)
        idx += 1
    
outfile.close()
