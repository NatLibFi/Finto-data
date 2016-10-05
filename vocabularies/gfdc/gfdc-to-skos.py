#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys
import re

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <csvfile>" % sys.argv[0]
    sys.exit(1)

csvfile = sys.argv[1]

GFDC = Namespace("http://urn.fi/URN:NBN:fi:au:gfdc:")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('gfdc', GFDC)

def class_uri(notation):
    return GFDC['C' + notation]

def add_class(notation, labelEn, labelFi, labelDe, labelFr):
    uri = class_uri(notation)
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.notation, Literal(notation)))
    if labelEn != '' and labelEn != 'MISSING_VALUE':
        g.add((uri, SKOS.prefLabel, Literal(labelEn, 'en')))
    if labelFi != '' and labelFi != 'MISSING_VALUE':
        g.add((uri, SKOS.prefLabel, Literal(labelFi, 'fi')))
    if labelDe != '' and labelDe != 'MISSING_VALUE':
        g.add((uri, SKOS.prefLabel, Literal(labelDe, 'de')))
    if labelFr != '' and labelFr != 'MISSING_VALUE':
        g.add((uri, SKOS.prefLabel, Literal(labelFr, 'fr')))
    
    parent = notation[:-1]
    if parent.endswith('.'):
        parent = parent[:-1]
    if parent != '':
        g.add((uri, SKOS.broader, class_uri(parent)))
        g.add((class_uri(parent), SKOS.narrower, uri))
    else:
        g.add((uri, SKOS.topConceptOf, GFDC['']))
        g.add((GFDC[''], SKOS.hasTopConcept, uri))


with open(csvfile, 'rb') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        add_class(row['fdcNumber'].strip(),
                  row['prefLabel-eng'].strip(),
                  row['prefLabel-fin'].strip(),
                  row['prefLabel-ger'].strip(),
                  row['prefLabel-fre'].strip())

g.serialize(destination=sys.stdout, format='turtle')
