#!/usr/bin/env python
import rdflib, sys
from rdflib import Graph, Namespace, RDF

skos = Namespace("http://www.w3.org/2004/02/skos/core#")
ysometa = Namespace("http://www.yso.fi/onto/yso-meta/2007-03-02/")
om = Namespace("http://www.yso.fi/onto/yso-peilaus/2007-03-02/")

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s <yso-input-file> <output-filename.ttl>" % sys.argv[0]
    sys.exit(1)

yso = Graph().parse(sys.argv[1])

def convert_matches(matches, onto):
    for match in matches:
        if len(matches) > 1:
            onto.add( (conc, skos.closeMatch, match) )
        else:
            onto.add( (conc, skos.exactMatch, match) )
        onto.remove( (conc, om.definedConcept, match) )


for conc in yso.subjects(RDF.type, ysometa.Concept):
    ysa = []
    allars = []
    for match in yso.objects(conc, om.definedConcept):
        if "ysa/Y" in match:
            ysa.append(match)
        if "allars/Y" in match:
            allars.append(match)

    convert_matches(ysa, yso)
    convert_matches(allars, yso)

yso.serialize(sys.argv[2], format='turtle')

