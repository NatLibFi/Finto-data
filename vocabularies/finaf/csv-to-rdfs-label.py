#!/usr/bin/env python

import csv
import sys

NAMESPACES = {
  'rdaa': 'http://rdaregistry.info/Elements/a/',
  'rdap': 'http://rdaregistry.info/Elements/p/',
  'rdau': 'http://rdaregistry.info/Elements/u/'
}

reader = csv.DictReader(sys.stdin)
for row in reader:
    uri = row['RDA URI']
    labelSe = row['propLabelSe']
    for prefix, ns in NAMESPACES.items():
        uri = uri.replace(ns, prefix + ":")
    print()
    print(f'{uri} rdfs:label "{labelSe}"@se .')
