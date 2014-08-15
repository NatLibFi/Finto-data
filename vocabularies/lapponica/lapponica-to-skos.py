#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Namespace, Graph, RDF, RDFS, Literal, URIRef
import sys
import urllib
import re

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
OWL=Namespace("http://www.w3.org/2002/07/owl#")
LAP=Namespace("http://urn.fi/URN:NBN:fi:au:lapponica:")

infile=sys.argv[1]

conc=None
rel=None

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('owl', OWL)
g.namespace_manager.bind('lapponica', LAP)

# add custom types
g.add((LAP.OrgConcept, RDF.type, OWL.Class))
g.add((LAP.OrgConcept, RDFS.subClassOf, SKOS.Concept))
g.add((LAP.OrgConcept, RDFS.label, Literal(u"Yhteisö", "fi")))

g.add((LAP.GeoConcept, RDF.type, OWL.Class))
g.add((LAP.GeoConcept, RDFS.subClassOf, SKOS.Concept))
g.add((LAP.GeoConcept, RDFS.label, Literal(u"Maantieteellinen asiasana", "fi")))

labelmap = {}
counter = 1

def label2uri(label):
  global counter
  if label not in labelmap:
    # mint new URI
    labelmap[label] = LAP["L%d" % counter]
    counter += 1
  return labelmap[label]

for line in open(infile):
  line = line.decode('latin1').strip()
  line = ' '.join(line.split()) # collapse whitespace

  if line == '': # empty line between concepts
    conc=rel=None
    continue
  
  if line.startswith('LAPPONICA'):
    continue # header not to be confused with concepts

  if line.startswith('LT'):
    rel=SKOS.broader
    line = line[2:].strip()
  elif line.startswith('ST'):
    rel=SKOS.narrower
    line = line[2:].strip()
  elif line.startswith('RT'):
    rel=SKOS.related
    line = line[2:].strip()
  elif line.startswith('KT'):
    rel=SKOS.altLabel
    line = line[2:].strip()
  elif line.startswith(u'KÄ'): continue

  if rel is None:
    label = line
    type = None
    m = re.match(r'(.*) +\(([YP])\)', line)
    if m:
      label = m.group(1)
      type = m.group(2)
    
    conc = label2uri(label)
    g.add((conc, RDF.type, SKOS.Concept))
    g.add((conc, SKOS.prefLabel, Literal(label, 'fi')))
    if type == 'Y':
      g.add((conc, RDF.type, LAP.OrgConcept))
    elif type == 'P':
      g.add((conc, RDF.type, LAP.GeoConcept))
      
    continue
  
  if rel == SKOS.altLabel:
    m = re.match(r'(.*) +\(([YP])\)', line)
    if m:
      line = m.group(1)
    target = Literal(line, 'fi')
  else:
    target = label2uri(line)
  
  g.add((conc, rel, target))
  
  
g.serialize(destination=sys.stdout, format='turtle')  
