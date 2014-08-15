#!/usr/bin/env python

from rdflib import Graph, URIRef, Namespace, Literal, RDF, RDFS
from lxml import etree
from lxml.etree import QName
import sys

# RDF namespaces
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
PAIKAT=Namespace("http://www.yso.fi/onto/paikat/")
GEO=Namespace("http://www.opengis.net/ont/geosparql#")

# XML namespaces
PNR="http://xml.nls.fi/Nimisto/Nimistorekisteri/2009/02"
GML="http://www.opengis.net/gml"

# map to 2 character language codes if possible
LANGMAP={
  'fin': 'fi',
  'swe': 'sv',
}

# function from http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def convert(elem):
  scale = int(elem.findtext(QName(PNR, 'mittakaavarelevanssiKoodi')))
  if scale >= 250000: # 250000 and above ~ 60000 places
    id = elem.findtext(QName(PNR, 'paikkaID'))
    type = elem.findtext(QName(PNR, 'paikkatyyppiKoodi'))
    uri = PAIKAT["P" + id]
    g.add((uri, RDF.type, PAIKAT['T' + type]))
    g.add((uri, RDF.type, SKOS.Concept))
    
    point = URIRef(uri + "_point")
    g.add((uri, GEO.hasGeometry, point))
    g.add((point, RDF.type, GEO.Point))
    coords = elem.findtext("{%s}paikkaSijainti//{%s}pos" % (PNR, GML))
    wkt = "<http://www.opengis.net/def/crs/EPSG/0/3067> POINT(%s)" % coords
    g.add((point, GEO.asWKT, Literal(wkt, datatype=GEO.wktLiteral)))
    for name in elem.findall("{%s}nimi/{%s}PaikanNimi" % (PNR, PNR)):
      label = name.findtext(QName(PNR, 'kirjoitusasu'))
      lang = name.findtext(QName(PNR, 'kieliKoodi'))
      lang = LANGMAP.get(lang, lang)
      g.add((uri, SKOS.prefLabel, Literal(label, lang)))
      
    

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('paikat', PAIKAT)
g.namespace_manager.bind('geo', GEO)

paikat = etree.iterparse('paikka.xml', events=('end',), tag=QName(PNR, 'Paikka'))
fast_iter(paikat, convert)

g.serialize(format='turtle', destination=sys.stdout)
