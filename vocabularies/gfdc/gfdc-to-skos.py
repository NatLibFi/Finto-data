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

# map 3-letter ISO 639-2 language codes to 2-letter 639-1 codes used in RDF
LANGMAP = {
    'eng': 'en',
    'fin': 'fi',
    'ger': 'de',
    'fre': 'fr'
}

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('gfdc', GFDC)

def class_uri(notation):
    return GFDC['C' + notation]

def add_class(notation, labels, includingNotes, scopeNotes):
    uri = class_uri(notation)
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.notation, Literal(notation)))
    for lang3, lang2 in LANGMAP.items():
        if labels[lang3] != '' and labels[lang3] != 'MISSING_VALUE':
            g.add((uri, SKOS.prefLabel, Literal(labels[lang3], lang2)))
        if includingNotes[lang3] != '':
            g.add((uri, SKOS.scopeNote, Literal(includingNotes[lang3], lang2)))
        if scopeNotes[lang3] != '':
            g.add((uri, SKOS.scopeNote, Literal(scopeNotes[lang3], lang2)))
    
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
        labels = {}
        includingNotes = {}
        scopeNotes = {}
        for lang in LANGMAP.keys():
            labels[lang] = row['prefLabel-%s' % lang].strip()
            includingNotes[lang] = row['includingNote-%s' % lang].strip()
            scopeNotes[lang] = row['scopeNote-%s' % lang].strip()
        add_class(row['fdcNumber'].strip(), labels, includingNotes, scopeNotes)

g.serialize(destination=sys.stdout, format='turtle')
