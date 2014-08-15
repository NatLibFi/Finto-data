#!/usr/bin/env python

import sys
from rdflib import Graph, Namespace, RDF
from rdflib.util import guess_format

# namespaces
TERO = Namespace("http://www.yso.fi/onto/tero/")
YSO = Namespace("http://www.yso.fi/onto/yso/")
TEROYSO = Namespace("http://www.yso.fi/onto/tero/p")
TEROMETA = Namespace("http://www.yso.fi/onto/tero-meta/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# input graph  
g = Graph()
for fn in sys.argv[1:]:
  g.parse(fn, format=guess_format(fn))
  
g.namespace_manager.bind('tero',TERO)
g.namespace_manager.bind('terometa',TEROMETA)

out = Graph()
for prefix,ns in g.namespace_manager.namespaces():
  out.namespace_manager.bind(prefix,ns)

def switch(res):
  if res.startswith(TEROYSO):
    return YSO[res.replace(TEROYSO, 'p')]
  return res

for s,p,o in g:
  out.add((switch(s), p, switch(o)))

out.serialize(destination=sys.stdout, format='turtle')
