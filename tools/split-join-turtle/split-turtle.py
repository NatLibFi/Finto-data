#!/usr/bin/env python

import argparse
import zlib
import sys

def matches(string, datastr, index):
    substr = datastr[index:index+len(string)]
    return substr.lower() == string.lower()

def can_split(last_block, blockiness):
    checksum = zlib.crc32(last_block.encode('UTF-8'))
    return (checksum % blockiness) == 0

def open_slice(slice, prefixes):
    outfile = open("{}{:03d}.ttl".format(args.basename, slice), 'w')
    for prefix in prefixes:
        print(prefix, file=outfile)
    print("", file=outfile)
    return outfile

parser = argparse.ArgumentParser(description="Split a Turtle file into slices")
parser.add_argument("-c", "--chars", type=int, help="approximate number of characters per slice", default=10000000)
parser.add_argument("-b", "--blockiness", type=int, help="blockiness factor - larger values result in fewer splits", default=32)
parser.add_argument("basename", type=str, help="output file base name")
args = parser.parse_args()

data = sys.stdin.read()

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
last_split = last_block = idx

outfile = open_slice(slice, prefixes)
    
# actual data
while idx < len(data):
    if matches('\n\n', data, idx):
        
        if (idx - last_split) >= args.chars \
           and can_split(data[last_block:idx], args.blockiness):
            print("", file=outfile)
            outfile.close()
            last_split = idx
            slice += 1
            outfile = open_slice(slice, prefixes)
        else:
            last_block = idx
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
