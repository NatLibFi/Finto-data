#!/usr/bin/env python

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS

import csv
import sys
import re

MATCHTYPES = ('closeMatch', 'exactMatch')

g = Graph()
g.namespace_manager.bind('skos', SKOS)
reader = csv.reader(open(sys.argv[1]))
for idx, row in enumerate(reader):
    if idx == 0:
        continue # skip header
    lapuri = row[1].strip()
    matchtype = row[5].strip()
    ysouri = row[7].strip()
    
    if lapuri != '' and matchtype in MATCHTYPES and ysouri != '':
        g.add((URIRef(lapuri), SKOS[matchtype], URIRef(ysouri)))

g.serialize(destination=sys.stdout, format='turtle')
    
    
