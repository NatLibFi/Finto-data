#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCN = Namespace("http://cv.iptc.org/newscodes/scene/")

g = Graph()
g.namespace_manager.bind('skos', SKOS)

reader = csv.reader(open(sys.argv[1]))
idx = 0
for row in reader:
  idx += 1
  if idx < 2: continue
  code = '%06d' % int(row[5])
  label = row[2].strip().decode('UTF-8')
  uri = SCN[code]
  g.add((uri, SKOS.prefLabel, Literal(label, 'fi')))
  
g.serialize(destination=sys.stdout, format='turtle')
