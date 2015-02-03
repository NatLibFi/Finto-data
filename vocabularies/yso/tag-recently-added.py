#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, BNode

# namespaces
YSOMETA = Namespace("http://www.yso.fi/onto/yso-meta/2007-03-02/")
YSOUPDATE = Namespace("http://www.yso.fi/onto/yso-update/")

g = Graph()
g.parse(sys.argv[1])

qres = g.query(
    """SELECT DISTINCT ?subject
       WHERE
       {
         {
           # itsessään käsittelemättömät
           ?subject rdfs:subClassOf yso-update:uudet .
           ?subject rdfs:subClassOf yso-update:uudetSv .
         }
         UNION
         {  
           # orvoiksi jäävät, jos käsittelemättömät jätetään pois
           ?subject rdfs:subClassOf+ yso-update:uudet .
           ?subject rdfs:subClassOf yso-update:uudetSv .
           FILTER NOT EXISTS {
             ?subject rdfs:subClassOf ?parent .
             FILTER (?parent != yso-update:uudet)
             FILTER (?parent != yso-update:uudetSv)
             FILTER NOT EXISTS { ?parent rdfs:subClassOf+ yso-update:uudet }
           }
         }
       }""")

for row in qres:
  conc = row.subject
  print >>sys.stderr, "tagging %s as StructuringClass" % conc
  g.add((conc, RDF.type, YSOMETA.StructuringClass))

g.serialize(destination=sys.stdout, format='turtle')
