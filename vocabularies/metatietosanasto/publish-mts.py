#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
import sys

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")


g = Graph()
g.parse(sys.argv[1], format='turtle')
g.parse('rdam.ttl', format='turtle')

for prop in g.subjects(RDF.type, RDF.Property):
  # esimerkki-instanssit jotka käyttävät tätä?
  for inst,val in g.subject_objects(prop):
    # esimerkki-instanssin luokka?
    cl = g.value(inst, RDF.type, None)
    
    g.add((cl, RDF.type, SKOS.Concept))
    g.add((prop, RDF.type, SKOS.Concept))
    g.add((val, SKOS.broader, prop))
    g.add((prop, SKOS.broader, cl))

g.serialize(destination=sys.stdout, format='turtle')
