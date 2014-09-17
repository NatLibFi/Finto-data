#!/usr/bin/env python

import sys
from rdflib import *
import ConfigParser
import argparse


# Removes previous owl:Ontology instances and replaces them with the baseURI
# Parameters:
# baseuri: concept (URIRef) to be stated as the owl:Ontology instance
# onto: graph containing the ontology
def fix_onto_definition(baseuri, onto):
  for s in g.subjects(RDF.type, OWL.Ontology):
    # Removes the previous owl:Ontology instances
    # having several owl:Ontology instances in the same file prevents TBC
    # to show the values and namespaces of the ontology correctly
    for p,o in g.predicate_objects(s):
      g.remove((s, p, o))
      print("Removed triple: <%s> <%s> <%s>") % (str(s), str(p), str(o))
    
    # Adding the correct baseURI and stating it to be an ontology instance
    g.add((baseuri, RDF.type, OWL.Ontology))


# Replaces the occurances of the old property with the new property and removes
# the old property from the ontology
def replace_property(pold, pnew, onto):
  print("Replaced property <%s> with <%s>") % (str(pold), str(pnew))

  i = 0
  # Adding the values
  for s,o in g.subject_objects(pold):
    g.add((s, pnew, o))
    i += 1
  
  print("Added %d triples") % i
  
  # Removing the old property
  remove_resource(pold, onto)

# Removing all instances of the concept (=URIRef) p in the ontology
def remove_resource(prop, onto):
  i = 0
  for p,o in g.predicate_objects(prop):
    g.remove((prop,p,o))
    i += 1

  print("Removed %d triples: <%s> ? ?") % (i, str(prop))
  
  i = 0
  for s,o in g.subject_objects(prop):
    g.remove((s,prop,o))
    i += 1

  print("Removed %d triples: ? <%s> ?") % (i, str(prop))

  i = 0
  for s,p in g.subject_predicates(prop):
    g.remove((s,p,prop))
    i += 1

  print("Removed %d triples: ? ? <%s>") % (i, str(prop))
 
  print("---")


####################################################################
parser = argparse.ArgumentParser()
parser.add_argument("configfile", help="file containing the terms of the matched vocabulary")
parser.add_argument("inputonto", help="the ontology which is to be made TBC compatible")
parser.add_argument("outputonto", help="path for the TBC-combatible ontology")
args = parser.parse_args()


Config = ConfigParser.ConfigParser()
Config.read(args.configfile)

g = Graph()
g.parse(args.inputonto, format='n3')


# Replacing prefLabel, altLabel and hiddenLabel
# This enables the labels in the hierarchy and search to work in TBC
replace_property(URIRef(Config.get('prefLabel', 'old')), URIRef(Config.get('prefLabel', 'new')), g)
replace_property(URIRef(Config.get('altLabel', 'old')), URIRef(Config.get('altLabel', 'new')), g)
replace_property(URIRef(Config.get('hiddenLabel', 'old')), URIRef(Config.get('hiddenLabel', 'new')), g)


# Adding an ontology instance statement to the ontology
baseuri = Config.get('ontology', 'baseuri')
fix_onto_definition(URIRef(baseuri), g)


# Removing unnecessary properties
for option in Config.options('remove'):
  remove_resource(URIRef(Config.get('remove', option)), g)


g.serialize(args.outputonto, format='turtle')
