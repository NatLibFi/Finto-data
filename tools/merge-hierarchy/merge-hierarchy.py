#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Enrich the subclass hierarchy by making sure that all concepts that
# have an outgoing owl:equivalentClass relationship also have
# rdfs:subClassOf relationships to parents of the equivalent class.
# e.g. A1 equivalentClass A2 . A2 rdfs:subClassOf B .
#   -> A1 rdfs:subClassOf B


import sys
from rdflib import Graph, Namespace, RDFS
import rdflib.util

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
OWL=Namespace("http://www.w3.org/2002/07/owl#")

g = Graph()
g.parse(sys.argv[1], format=rdflib.util.guess_format(sys.argv[1]))

for s,o in g.subject_objects(OWL.equivalentClass):
    for parent in g.objects(o, RDFS.subClassOf):
        g.add((s, RDFS.subClassOf, parent))

g.serialize(destination=sys.stdout, format='turtle')

    
