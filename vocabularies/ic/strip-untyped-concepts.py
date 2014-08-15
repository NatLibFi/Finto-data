#!/usr/bin/env python

from rdflib import Graph, Namespace, RDF
import sys

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.parse(sys.argv[1], format='turtle')

for prop in (SKOS.broader, SKOS.narrower):
  for s,o in g.subject_objects(prop):
    if (s, RDF.type, SKOS.Concept) not in g:
      g.remove((s,prop,o))
    if (o, RDF.type, SKOS.Concept) not in g:
      g.remove((s,prop,o))

g.serialize(destination=sys.stdout, format='turtle')
