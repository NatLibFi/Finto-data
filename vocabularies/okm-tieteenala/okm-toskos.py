#!/usr/bin/env python

import sys
import re
from rdflib import *

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
OKM = Namespace("http://www.yso.fi/onto/okm-tieteenala/")

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('okm', OKM)

data = open(sys.argv[1]).read()
# strip page numbers
data = re.sub(r'\d \(\d\)', '', data)
# strip empty lines
data = re.sub(r'\n\s*\n', '\n', data)

tmp, defs, docs = re.split('Liite \d', data) 
defs = defs.strip().split('\n')
docs = docs.strip().split('\n')

cs = OKM.conceptscheme
g.add((cs, RDF.type, SKOS.ConceptScheme))
g.add((cs, RDFS.label, Literal(defs[1], 'fi')))

for line in defs[3:]:
  tk, okm = re.split('\s{3,}', line)
  m = re.match('(\d+(?:,\d)?) (.*)', okm)
  code = m.group(1)
  uri = OKM["ta" + code.replace(',','')]
  label = m.group(2)
  g.add((uri, RDF.type, SKOS.Concept))
  g.add((uri, SKOS.notation, Literal(code)))
  g.add((uri, SKOS.prefLabel, Literal(label, 'fi')))
  g.add((uri, SKOS.inScheme, cs))
  if len(code) > 1:
    broader = OKM["ta" + code[0]]
    g.add((uri, SKOS.broader, broader))
  else:
    g.add((cs, SKOS.hasTopConcept, uri))
    g.add((uri, SKOS.topConceptOf, cs))

def jointext(text):
  text = '\n'.join(text)
  return text.replace('-\n', '').replace('\n', ' ')

code = None
text = []
for line in docs[3:]:
  m = re.match(r'([\d ,]+) (.*)', line)
  if m:
    if code and len(text) > 0:
      uri = OKM["ta" + code.replace(',', '').replace(' ', '')]
      g.add((uri, SKOS.scopeNote, Literal(jointext(text), 'fi')))
    
    text = []
    code = m.group(1)
  else:
    text.append(line)

# add en,sv labels
import csv

fieldnames = ['tid','tfi','ten','tsv','cid','cfi','cen','csv']
reader = csv.DictReader(open(sys.argv[2], 'r'), fieldnames=fieldnames)
for rec in reader:
  try:
    tid = int(rec['tid'])
  except ValueError:
    continue
  
  turi = OKM['ta%d' % tid]
  g.add((turi, SKOS.prefLabel, Literal(rec['ten'].strip(), 'en')))
  g.add((turi, SKOS.prefLabel, Literal(rec['tsv'].strip(), 'sv')))

  try:
    cid = int(rec['cid'])
  except ValueError:
    continue
  
  curi = OKM['ta%d' % cid]
  g.add((curi, SKOS.prefLabel, Literal(rec['cen'].strip(), 'en')))
  g.add((curi, SKOS.prefLabel, Literal(rec['csv'].strip(), 'sv')))

g.serialize(format='turtle', destination=sys.stdout)
