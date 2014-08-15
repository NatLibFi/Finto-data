#!/usr/bin/env python

from rdflib import Graph, URIRef, Namespace, Literal, RDF, RDFS
from lxml import etree
from lxml.etree import QName
import sys
import datetime

# RDF namespaces
OWL=Namespace("http://www.w3.org/2002/07/owl#")
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
PAIKAT=Namespace("http://www.yso.fi/onto/paikat/")
DCT=Namespace("http://purl.org/dc/terms/")

# XML namespaces
GMD="http://www.isotc211.org/2005/gmd"
GCO="http://www.isotc211.org/2005/gco"
XML="http://www.w3.org/XML/1998/namespace"
XSD="http://www.w3.org/2001/XMLSchema"

LANGMAP={
  '#SW': 'sv',
  '#EN': 'en',
}

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('paikat', PAIKAT)
g.namespace_manager.bind('dct', DCT)

cs = PAIKAT['conceptscheme']
g.add((cs, RDF.type, SKOS.ConceptScheme))

metadata = etree.parse('metadata.xml')
root = metadata.getroot()
abstract = root.find('.//{%s}abstract' % GMD)
abs_fi = abstract.findtext('{%s}CharacterString' % GCO)
g.add((cs, DCT.description, Literal(abs_fi, 'fi')))
for abs in abstract.findall('.//{%s}LocalisedCharacterString' % GMD):
  lang = LANGMAP[abs.get('locale')]
  g.add((cs, DCT.description, Literal(abs.text, lang)))

rights_fi = root.findtext('.//{%s}resourceConstraints//{%s}CharacterString' % (GMD, GCO))
g.add((cs, DCT.rights, Literal(rights_fi, 'fi')))

orgname = root.find('.//{%s}organisationName' % GMD)
org_fi = orgname.findtext('{%s}CharacterString' % GCO)
g.add((cs, DCT.publisher, Literal(org_fi, 'fi')))
for org in orgname.findall('.//{%s}LocalisedCharacterString' % GMD):
  lang = LANGMAP[org.get('locale')]
  g.add((cs, DCT.publisher, Literal(org.text, lang)))

todayiso = datetime.date.today().isoformat()
g.add((cs, DCT.date, Literal(todayiso)))

#for enum in root.findall('.//{%s}enumeration' % XSD):
#  id = enum.get('value')
#  uri = PAIKAT['T_' + id]
#  for doc in enum.findall('.//{%s}documentation' % XSD):
#    label = doc.text
#    lang = LANGMAP[doc.get('{%s}lang' % XML)]
#    g.add((uri, RDF.type, OWL.Class))
#    g.add((uri, RDFS.subClassOf, SKOS.Concept))
#    g.add((uri, RDFS.label, Literal(label, lang)))
    

g.serialize(format='turtle', destination=sys.stdout)
