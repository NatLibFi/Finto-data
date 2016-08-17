#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, rdflib
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
from unidecode import unidecode

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")

graph = Graph()
graph.parse(sys.argv[1], format='turtle')

for s,p,o in graph.triples( (None, rdflib.RDF.type, SKOS.Concept) ):
    result = graph.preferredLabel(s, lang='fi')
    if result:
        label = result[-1][-1].value
        stripped = unidecode(label)
        if label != stripped and 'ä'.decode('utf-8') not in label and 'ö'.decode('utf-8') not in label:
          graph.add((s, SKOS.hiddenLabel, Literal(stripped)))

graph.serialize(format='turtle', destination=sys.stdout)
