#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SC = Namespace("http://cv.iptc.org/newscodes/subjectcode/")

g = Graph()
g.namespace_manager.bind('skos', SKOS)

reader = csv.reader(open(sys.argv[1]))
idx = 0
for row in reader:
  idx += 1
  if idx < 3: continue
  for code in row[:4]:
    if code != '': break
  label = row[4].strip().decode('UTF-8')
  defn = row[5].strip().decode('UTF-8')
  uri = SC[code.strip()]
  g.add((uri, SKOS.prefLabel, Literal(label, 'fi')))
  if defn != '':
    g.add((uri, SKOS.definition, Literal(defn, 'fi')))
  
g.serialize(destination=sys.stdout, format='turtle')
