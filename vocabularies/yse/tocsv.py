#!/usr/bin/env python

import pymarc
import csv
import sys


def format_timestamp(ts):
    year = int(ts[0:2])
    if year >= 80:
        year += 1900
    else:
        year += 2000
    mon = int(ts[2:4])
    day = int(ts[4:6])
    return "%04d-%02d-%02d" % (year, mon, day)

input = open(sys.argv[1], 'rb')
reader = pymarc.MARCReader(input)

writer = csv.writer(sys.stdout)
writer.writerow(['id', 'created', 'modified', 
    'term (150)', 'alt (450)', 'groups (072)',
    'ednote (667)', 'source (670)', 'note (680)'])

for rec in reader:
    # record id (001)
    rid = rec['001'].value()
    
    # created (008)
    created = format_timestamp(rec['008'].value()[:6])
    
    # modified (005)
    modified = format_timestamp(rec['005'].value()[2:8])

    # term
    term = rec['150']['a'].encode('UTF-8')
    
    # altlabels
    altlabels = []
    for f in rec.get_fields('450'):
        altlabels.append(f['a'].encode('UTF-8'))
    
    # groups (072)
    groups = []
    for f in rec.get_fields('072'):
        groupid = f['a'][3:].strip()
        if groupid != '':
            groups.append(groupid)
    
    # editorial note (667)
    if '667' in rec:
        ednote = rec['667'].value().encode('UTF-8')
    else:
        ednote = ''

    # source (670)
    if '670' in rec:
        source = rec['670'].value().encode('UTF-8')
    else:
        source = ''
    
    # note (680)
    if '680' in rec:
        note = rec['680'].value().encode('UTF-8')
    else:
        note = ''
    
    writer.writerow([rid, created, modified, 
        term, ', '.join(altlabels), ', '.join(groups),
        ednote, source, note])
