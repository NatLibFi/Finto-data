#!/usr/bin/env python3

# Utility to merge timestamp files in case they get out of sync, as happened in June 2017.
# Goes through the Git history of timestamps.tsv and keeps the last entry for each URI,
# except when that would cause loss of information (date changed to "-").
# Duplicate overrides are logged on stderr.

import sys
import subprocess

commitlog = subprocess.check_output(['git', 'log', '--pretty=oneline', 'timestamps.tsv'])
commits = [cinfo.split()[0].decode('UTF-8') for cinfo in commitlog.splitlines()]
commits.reverse()

data = {}

def process_tsdata(commit, tsdata):
    tslines = tsdata.splitlines()
    lines_with_dates = [line for line in tslines if "\t201" in line]
    print("Processing commit {}, lines={}, dates={}".format(commit, len(tslines), len(lines_with_dates)), file=sys.stderr)
    for line in tslines:
        line = line.strip()
        uri, newcs, newts = line.split('\t')
        if uri in data:
            oldline = data[uri]
            if oldline == line:
                continue  # no change
            lname = uri.split('/')[-1]
            oldcs, oldts = oldline.split()[1:]
            if oldcs == newcs and newts == '-':
                print(commit, "NOT overriding", lname, "{} -> {}".format(oldcs, newcs), "{} -> {}".format(oldts, newts), file=sys.stderr)
                continue
            print(commit, "Overriding", lname, "{} -> {}".format(oldcs, newcs), "{} -> {}".format(oldts, newts), file=sys.stderr)
        data[uri] = line


for commit in commits:
    tsdata = subprocess.check_output(['git', 'show', '{}:./timestamps.tsv'.format(commit)])
    tsdata = tsdata.decode('UTF-8')
    process_tsdata(commit, tsdata)


for uri in sorted(data.keys()):
    print(data[uri])
