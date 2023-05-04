#!/usr/bin/env python3

# Utility to combine timestamp information from two timestamp files.
# * Hashes for concepts will be read from the first file.
# * All other information will be read from the second file.
# * Combined results will be printed on stdout.

# This can be useful in a situation where the hashing algorithm needs to be
# changed, as happened in April 2023, when an upgrade of rdflib triggered
# changes in N-Triples output and thus affected all hashes.

import sys

data = {}  # key: concept URI, value: dict with keys uri, hash, mtime, ctime

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} <timestamp-hashes.tsv> <timestamp-data.tsv>")
    sys.exit(1)

hashfile = sys.argv[1]
datafile = sys.argv[2]

with open(datafile) as dataf:
    for line in dataf:
        uri, hash, mtime, ctime = line.strip().split('\t')
        data[uri] = {'uri': uri, 'hash': hash, 'mtime': mtime, 'ctime': ctime}

with open(hashfile) as hashf:
    for line in hashf:
        uri, hash, _, _ = line.strip().split('\t')
        data[uri]['hash'] = hash

for uri, cdata in data.items():
    print(f"{uri}\t{cdata['hash']}\t{cdata['mtime']}\t{cdata['ctime']}")
