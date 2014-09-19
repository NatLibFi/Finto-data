#!/usr/bin/env python3

import argparse
import configparser
from term_in_onto import *
from rdflib import *
import csv
import re

def read_terms(path):
  f = open(path)
  r = csv.reader(f)

  d = {}
  for line in r:
    first = True
    fi = ""
    for term in line:
      t = pstrip(term)
      if first:
        fi = t
        d[fi] = []
        first = False
      else:
        d[fi].append(t)


  return d  

# TODO: is this used anywhere?!
def add_term(term, source, dic):
  if term not in dic:
    dic[term] = set()
  dic[term].add(source)



def create_uri(term, baseuri, onto):
  
  localname = term.replace("ä", "a")
  localname = localname.replace("ö", "o")
  localname = localname.replace("å", "a")
  localname = re.sub('[^0-9a-zA-Z]+', '_', localname)


  uri = baseuri + localname
  used = False

  for i in onto.predicate_objects(URIRef(uri)):
    used = True
    break

  if used: 
    used = True

    while used:
      i = 1
      uri = baseuri + localname + str(i)
      used = False

      for i in onto.predicate_objects(URIRef(uri)):
        used = True
        break
  return uri

def add_vocab_term(term_uri, vocab_uri, type_uri, onto):
  onto.add((URIRef(term_uri), OWL.subClassOf, URIRef(vocab_uri)))
  onto.add((URIRef(term_uri), RDF.type, URIRef(type_uri)))

  
def add_term_data(term_uri, term, langvar, vocab, onto):
  DC = Namespace("http://purl.org/dc/elements/1.1/")
  SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

  
  onto.add((URIRef(term_uri), DC.source, Literal(vocab, lang="fi")))
  if len(term) > 0:
    onto.add((URIRef(term_uri), SKOS.prefLabel, Literal(term, lang="fi")))
  
  if len(langvar) > 0:
    term = langvar[0]
    if len(term) > 0:
      onto.add((URIRef(term_uri), SKOS.prefLabel, Literal(term, lang="sv")))
  if len(langvar) > 1:
    term = langvar[1]
    if len(term) > 0:
      onto.add((URIRef(term_uri), SKOS.prefLabel, Literal(term, lang="en")))
    


parser = argparse.ArgumentParser()
parser.add_argument("configfile", help="file containing the paths of input files and other configurations")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.configfile)

ontolemmas = read_lemmas(config.get('general', 'onto-lemmas'))

g = Graph()
g.parse(config.get('general', 'domainonto'), format='n3')

baseuri = config.get('general','baseuri')
typeuri = config.get('general','type')
vocabid = config.get('general','vocabid')


yso_found = {}
added = {}
lemmas = {}

for vocab in config.sections():
  if vocab == "general":
    continue
  
  vocab_uri = baseuri+vocab
  g.add((URIRef(vocab_uri), RDF.type, URIRef(typeuri)))
  
  terms = read_terms(config.get(vocab, 'termfile'))

  for term in terms:
    lemma = lemmatize(term)
#    if term in added:
#      add_term_data(added[term], term, terms[term], vocab, g)
#      continue
#
#    if term in lemmas:
#      add_term_data(lemmas[term], term, terms[term], vocab, g)
#      continue
#
#
    if lookup(term, vocabid) or lemma in ontolemmas:
      if term not in yso_found:
        yso_found[term] = set()
      yso_found[term].add(vocab)
      continue
    

    if term in added:
      uri = added[term]
    elif lemma in lemmas:
      uri = lemmas[lemma]
    else:
      uri = create_uri(term, baseuri, g)
      added[term] = uri
      lemmas[lemma] = uri
      add_vocab_term(uri, vocab_uri, typeuri, g)

    add_term_data(uri, term, terms[term], vocab, g)

     

print("------------")
print("vocab-duplicate")
for i in yso_found:
  print(str(i) + ":::" + str(yso_found[i]))

for i in added:
  print(str(i) + ":::" + str(added[i]))
g.serialize(config.get('general','outonto'), format='turtle')
