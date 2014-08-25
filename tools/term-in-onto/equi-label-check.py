#!/usr/bin/env python3
# coding: utf-8
import csv, json, urllib, codecs, sys, operator, time
from urllib.request import urlopen
from urllib.parse import urlencode
import argparse
from rdflib import plugin, Graph, URIRef, Namespace, RDF 
from rdflib.store import Store

# This scripts lists the concepts between two ontologies that have a common
# lemmatized label, but no equivalence connection between the concepts

parser = argparse.ArgumentParser()
parser.add_argument("tag1", help="tag for the 1st vocabulary. Used also for searching for equi connections in Finto")
parser.add_argument("lemmafile1", help="file containing lemmatized labels and URIs of the 1st vocabulary")
parser.add_argument("tag2", help="tag for the 2nd vocabulary")
parser.add_argument("lemmafile2", help="file containing lemmatized labels and URIs of the 2nd vocabulary")
args = parser.parse_args()

# Reading in the lemma-URI files
lemmas1 = read_lemmas(args.lemmafile1)
lemmas2 = read_lemmas(args.lemmafile2)

# set up connection to SPARQL endpoint
store = plugin.get('SPARQLStore',Store)('http://api.finto.fi/sparql')
# open a graph from SPARQL endpoint
g = Graph(store, URIRef('http://www.yso.fi/onto/' + args.tag1 + '/'))
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


for lemma in lemmas1:
  if lemma in lemmas2:
  # The same lemma is found in both of the ontologies

    for uri in lemmas1[lemma]:
      matchfound = False
      
      # Looping through the URIs seeing if there is an equivalence connection
      # with the concept containing the same lemma in the other ontology
      for equi in g.objects(URIRef(uri), SKOS.exactMatch):
        if str(equi) in lemmas2[lemma]:
          matchfound = True
      
      if not matchfound:
        # No equivalence found, so added to the list of same 
        print(lemma + "," + uri + "," + ",".join(lemmas2[lemma]))


exit(0)


