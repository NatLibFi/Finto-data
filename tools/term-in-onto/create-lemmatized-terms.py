#!/usr/bin/env python3

from rdflib import plugin, Graph, URIRef, Namespace, RDF
from rdflib.store import Store
import csv, urllib, codecs, sys, operator, time
from urllib.request import urlopen
from urllib.parse import urlencode
import argparse

def lemmatize(term):
  params = urlencode({ 'text': term , 'locale': 'fi'})
#  params = urlencode({ 'text': term.decode("utf8") , 'locale': 'fi'})
  url = seco_api + params 
  response = urlopen(url).readall().decode('utf-8')
  return pstrip(response)

# Strips whitespace and quotation marks
def pstrip(str):
  return str.strip('"\' \t\n')

# Concept type is optional; if it exists, only those concepts are chosen for lemmatizing
parser = argparse.ArgumentParser()
parser.add_argument("concepttype", nargs="?", help="the type of concepts that are accepted")
parser.add_argument("ontotag", help="tag for the ontology used in YSO URIs")
parser.add_argument("outputfile", help="file for printing the terms of the matched vocabulary")
args = parser.parse_args()


SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
seco_api = 'http://demo.seco.tkk.fi/las/baseform?'

# set up connection to SPARQL endpoint
store = plugin.get('SPARQLStore',Store)('http://api.finto.fi/sparql')
# open JUPO graph from SPARQL endpoint
g = Graph(store, URIRef('http://www.yso.fi/onto/' + args.ontotag + '/'))

# look up all the prefLabels
concs = g.subject_objects(SKOS.prefLabel)

# Dictionary for storing the lemmas and URIs
d = {}

different = 0
same = 0

if args.concepttype is not None:
  concept = URIRef(args.concepttype)


# List the lemmatized Finnish prefLabels and corresponding URIs
for (s,l) in list(concs):

  if args.concepttype is not None:
    typefound = False
    for o in list(g.objects(s, RDF.type)):
      if o == concept:
        # Of right type, so continue to lemmatization
        typefound = True
        break
    # Right type not found: don't lemmatize
    if not typefound:
      continue

  if l.language == "fi":
    lemma = lemmatize(str(l))
    if lemma in d:
      d[lemma].append(str(s))
    else:
      d[lemma] = [str(s)]
      if lemma == pstrip(l):
        same = same +1
      else:
        different = different + 1


# Write the lemmas and URIs to a file
f = open(args.outputfile, "w")
  
for val in d:
    
  first = True
  f.write(val)  

  for i in d[val]:
    f.write(",")
    f.write(i)
  f.write("\n")

print("same before and after lemmatizing: " + str(same))
print("different after lemmatizing: " + str(different))
