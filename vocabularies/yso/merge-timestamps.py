#!/usr/bin/env python

# Utility to merge timestamp files in case they get out of sync, as happened in June 2017.
# Takes lines of timestamp.tsv as input and keeps the last entry for each URI.
# Duplicate overrides are logged on stderr.

import sys

data = {}

for line in sys.stdin:
    line = line.strip()
    uri, checksum, date = line.split('\t')
    if uri in data:
        print >>sys.stderr, "overriding", uri
    data[uri] = line

for uri in sorted(data.keys()):
    print data[uri]
