#!/usr/bin/env python

from rdflib import Graph, URIRef, Namespace, Literal, RDF, RDFS
from lxml import etree
from lxml.etree import QName
import sys

# RDF namespaces
OWL=Namespace("http://www.w3.org/2002/07/owl#")
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
PAIKAT=Namespace("http://www.yso.fi/onto/paikat/")

# XML namespaces
XML="http://www.w3.org/XML/1998/namespace"
XSD="http://www.w3.org/2001/XMLSchema"

LANGMAP={
  'fin': 'fi',
  'swe': 'sv',
  'eng': 'en',
}

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('paikat', PAIKAT)

tyypit = etree.parse('paikkatyyppi.xsd')
root = tyypit.getroot()
for enum in root.findall('.//{%s}enumeration' % XSD):
  id = enum.get('value')
  uri = PAIKAT['T' + id]
  for doc in enum.findall('.//{%s}documentation' % XSD):
    label = doc.text
    lang = LANGMAP[doc.get('{%s}lang' % XML)]
    g.add((uri, RDF.type, OWL.Class))
    g.add((uri, RDFS.subClassOf, SKOS.Concept))
    g.add((uri, RDFS.label, Literal(label, lang)))
    

g.serialize(format='turtle', destination=sys.stdout)
