#!/usr/bin/env python3

import argparse
import sys

def matches(string, datastr, index):
    substr = datastr[index:index+len(string)]
    return substr.lower() == string.lower()

def extract_headers(data):
    headers = []
    idx = 0

    # prefix extraction
    while idx < len(data):
        if matches('@prefix', data, idx):
            start = idx
            idx += len('@prefix')
            while data[idx] != '\n':
                idx += 1
            headers.append(data[start:idx])
        elif matches('@base', data, idx):
            start = idx
            idx += len('@base')
            while data[idx] != '\n':
                idx += 1
            headers.append(data[start:idx])
        elif data[idx] == '#':
            while data[idx] != '\n':
                idx += 1
        elif data[idx] in ('\n', '\t', ' '):
            pass
        else:
            break
        idx += 1
    return (headers, idx)

headers_written = False
for filename in sys.argv[1:]:
    with open(filename) as infile:
        data = infile.read()
        headers, idx = extract_headers(data)
        if not headers_written:
            for header in headers:
                print(header)
            headers_written = True
        print("")
        print(data[idx:], end='')
