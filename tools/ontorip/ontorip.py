#!/usr/bin/env python

import sys
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, BNode
from rdflib.util import guess_format
from lxml import etree
import argparse

# parse arguments
parser = argparse.ArgumentParser(description='remove YSO from domain ontology. outputs the domain specific ontology on stdout')
parser.add_argument('input', type=str, help='input domain vocabulary')
parser.add_argument('--new', type=str, help='new YSO to add to the output')
parser.add_argument('--old', type=str, help='file in which to store old YSO')
parser.add_argument('--format', help='output format, e.g. turtle, xml, pretty-xml', default='turtle')
args = parser.parse_args()

# namespaces
OWL = Namespace("http://www.w3.org/2002/07/owl#")
YSO = Namespace("http://www.yso.fi/onto/yso/")
YSOMETA = Namespace("http://www.yso.fi/onto/yso-meta/2007-03-02/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")


try: # rdflib 2.4.x
  RDFNS = RDF.RDFNS
  RDFSNS = RDFS.RDFSNS
except: # rdflib 3.x
  RDFNS = RDF.uri
  RDFSNS = RDFS.uri

# input graph  
g = Graph()
g.parse(args.input, format=guess_format(args.input))

# output graph
out = Graph()
# copy prefix declarations to output graph
for prefix, ns in g.namespaces():
  out.namespace_manager.bind(prefix, ns)


def is_domainont(res):
  """Tries to figure out whether a URIref is part of a domain ontology.
     Anything that is YSO, YSOMETA, XSD, RDF, RDFS, OWL, SKOS, DC, DCT is not."""
  for non_domain_ns in (YSO, YSOMETA, XSD, RDFNS, RDFSNS, OWL, SKOS, DC, DCT):
    if res.startswith(non_domain_ns):
      return False
  return True


# find out the most common non-YSOMETA class
stats = {}	# key: class URIref val: count
for inst,cl in g.subject_objects(RDF.type):
  if not is_domainont(cl):
    continue
  stats.setdefault(cl, 0)
  stats[cl] += 1

stats = stats.items()
#print >>sys.stderr, "stats:", stats
stats.sort(key=lambda x:x[1], reverse=True)
seedclass = stats[0][0]
print >>sys.stderr, "Most common domain ontology class used as starting point:", seedclass

# Determine the bounds of the domain-specific ontology by performing a
# non-recursive breadth-first search (except a set is used instead of a FIFO
# so the traversal order is a bit random). Code adapted from Skosify.

to_search = set([seedclass])
seen = set()
while len(to_search) > 0:
  res = to_search.pop()
  if res in seen: continue
  seen.add(res)

  # res as subject
  for p,o in g.predicate_objects(res):
    out.add((res,p,o))
#    for cl in g.objects(res, RDF.type):
#      out.add((res,RDF.type,cl))

    if isinstance(p, URIRef) and p not in seen and is_domainont(p):
      to_search.add(p)
    if o not in seen:
      if isinstance(o, BNode) or (isinstance(o, URIRef) and is_domainont(o)):
        to_search.add(o)
  # res as predicate
#  for s,o in g.subject_objects(res):
#    out.add((s,res,o))
#    if isinstance(s, URIRef) and s not in seen and is_domainont(s):
#      to_search.add(s)
#    if isinstance(o, URIRef) and o not in seen and is_domainont(o):
#      to_search.add(o)
  # res as object
  for s,p in g.subject_predicates(res):
#    if not res.startswith(OWL): # ignore spurious owl:Class instances
    out.add((s,p,res))
#    for cl in g.objects(s, RDF.type):
#      out.add((s,RDF.type,cl))
    if s not in seen:
      if isinstance(s, BNode) or (isinstance(s, URIRef) and is_domainont(s)):
        to_search.add(s)
    if isinstance(p, URIRef) and p not in seen and is_domainont(p):
      to_search.add(p)

if args.old is not None:
  old = Graph()
  # copy namespace defs
  for prefix, ns in g.namespaces():
    old.namespace_manager.bind(prefix, ns)

  # copy all triples from input graph that were not in out (i.e. YSO only)
  for triple in g:
    if triple not in out:
      old.add(triple)
  oldf = open(args.old, 'w')
  old.serialize(destination=oldf, format=args.format)
  oldf.close()

if args.new is not None:
  out.parse(args.new, format=guess_format(args.new))

if 'xml' in args.format:
  rdfxml = out.serialize(format=args.format)

  # re-parse and re-serialize with lxml
  # to fix up namespaces stripped by rdflib serializer
  rdftree = etree.fromstring(rdfxml)
  nsmap = rdftree.nsmap
  for prefix,uri in out.namespaces():
    if prefix != '':
      nsmap[prefix] = uri
  newrdfelem = etree.Element("{%s}RDF" % RDFNS, nsmap=nsmap)
  for elem in rdftree:
    newrdfelem.append(elem)
  newrdftree = etree.ElementTree(newrdfelem)
  newrdftree.write(sys.stdout, pretty_print=True)
else:
  out.serialize(destination=sys.stdout, format=args.format)
