#!/usr/bin/env python

import sys
from rdflib import Graph, Namespace, RDF
from rdflib.util import guess_format

# namespaces
TERO = Namespace("http://www.yso.fi/onto/tero/")
TEROYSO = Namespace("http://www.yso.fi/onto/tero/p")
TEROMETA = Namespace("http://www.yso.fi/onto/tero-meta/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# input graph  
g = Graph()
for fn in sys.argv[1:]:
  g.parse(fn, format=guess_format(fn))

g.namespace_manager.bind('tero',TERO)
g.namespace_manager.bind('terometa',TEROMETA)

for conc in g.subjects(RDF.type, SKOS.Concept):
  if not conc.startswith(TEROYSO):
    g.add((conc, RDF.type, TEROMETA.Concept))

g.serialize(destination=sys.stdout, format='turtle')
