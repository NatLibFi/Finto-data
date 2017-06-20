#!/usr/bin/env python

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS

import csv
import sys
import re

g = Graph()
g.namespace_manager.bind('skos', SKOS)
reader = csv.reader(open(sys.argv[1]))
for idx, row in enumerate(reader):
    if idx == 0:
        continue # skip header
    uri = row[0].strip()
    label = row[2]
    label = re.sub(r'\([YSP]\)', '', label).strip()
    if label == '':
        continue
    g.add((URIRef(uri), SKOS.prefLabel, Literal(label, 'se')))

g.serialize(destination=sys.stdout, format='turtle')

    
    
