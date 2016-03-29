#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys
import re

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <csvfile>" % sys.argv[0]
    sys.exit(1)

csvfile = sys.argv[1]

PTVL = Namespace("http://urn.fi/URN:NBN:fi:au:ptvl:")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('ptvl', PTVL)

def add_concept(cell):
    notation, label = cell.split(" ", 1)
    if (notation.endswith('.')):
        notation = notation[:-1]
    uri = PTVL[notation]
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.notation, Literal(notation)))
    g.add((uri, SKOS.prefLabel, Literal(label, 'fi')))
    m = re.search('^\D+', notation)
    schemeid = m.group(0)
    if schemeid != 'P':
        schemeuri = PTVL[schemeid]
    else:
        schemeuri = PTVL['']
    g.add((uri, SKOS.inScheme, schemeuri))

    if '.' in notation:
        parent = notation.rsplit('.', 1)[0]
        parenturi = PTVL[parent]
        g.add((uri, SKOS.broader, parenturi))
        g.add((parenturi, SKOS.narrower, uri))
    else:
        g.add((uri, SKOS.topConceptOf, schemeuri))
        g.add((schemeuri, SKOS.hasTopConcept, uri))


with open(csvfile, 'rb') as cf:
    reader = csv.reader(cf)
    for row in reader:
        for cell in row:
            if cell.strip() != '':
                add_concept(cell.strip())

g.serialize(destination=sys.stdout, format='turtle')
