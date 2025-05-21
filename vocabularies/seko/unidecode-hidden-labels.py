#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, rdflib
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
from unidecode import unidecode

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")

def get_preferred_label(graph, subject, lang):
    for label in graph.objects(subject, SKOS.prefLabel):
        if label.language == lang:
            return label
    return None

graph = Graph()
graph.parse(sys.argv[1], format='turtle')

for s,p,o in graph.triples( (None, RDF.type, SKOS.Concept) ):
    result = get_preferred_label(graph, s, 'fi')
    if result:
        label = result.value
        stripped = unidecode(label)
        if label != stripped and 'ä' not in label and 'ö' not in label:
            graph.add((s, SKOS.altLabel, Literal(stripped, lang='fi')))
    for alt in graph.objects(s, SKOS.altLabel):
        stripped = unidecode(alt.value)
        if stripped != alt.value and 'ä' not in label and 'ö' not in label:
            graph.add((s, SKOS.hiddenLabel, Literal(stripped, lang='fi')))

graph.serialize(destination=sys.stdout.buffer, format='turtle')
