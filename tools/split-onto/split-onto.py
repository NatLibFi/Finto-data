#!/usr/bin/env python

from rdflib import *
import sys
import os.path

OWL = Namespace("http://www.w3.org/2002/07/owl#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
# note: the hash is omitted from the following namespace so that it
# will match the owl:Ontology instance URI
SKOSWITHOUTHASH = Namespace("http://www.w3.org/2004/02/skos/core")


if len(sys.argv) != 2:
  print >>sys.stderr, "Usage: %s ontology" % sys.argv[0]
  sys.exit(1)

g = Graph()
try:
  g.parse(sys.argv[1])
except:
  g.parse(sys.argv[1], format='turtle')

# output graphs
meta = Graph()
data = Graph()

# copy prefixes to meta graph
for prefix, uri in g.namespaces():
  meta.namespace_manager.bind(prefix, uri)

# output file names
basefn = os.path.splitext(sys.argv[1])[0]
metafn = basefn + "-meta.ttl"
datafn = basefn + "-data.nt"

typed_subjects = set([s for s, o in g.subject_objects(RDF.type)])
for subj in typed_subjects:
  types = g.objects(subj, RDF.type)
  is_meta = False
  for t in types:
    if t in (RDF.Property, RDFS.Class, OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty):
      is_meta = True
  
  for schema in (DC, DCT, SKOSWITHOUTHASH):
    if subj.startswith(schema):
      is_meta = True
  
  if is_meta:
    if isinstance(subj, BNode):
      continue # no point in adding blank nodes to the metadata graph
    outgraph = meta
  else:
    outgraph = data
  
  for p,o in g.predicate_objects(subj):
    outgraph.add((subj, p, o))

print len(g), len(meta), len(data), len(meta)+len(data)

meta.serialize(metafn, format='turtle')
data.serialize(datafn, format='nt')
