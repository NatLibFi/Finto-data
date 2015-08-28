#!/usr/bin/env python

import sys
import SPARQLWrapper
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <endpoint>" % sys.argv[0]
    sys.exit(1)
    
endpoint = sys.argv[1]

QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX pnrs: <http://ldf.fi/pnr-schema#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
SELECT * WHERE {
  GRAPH <http://www.yso.fi/onto/ysa/> {
    ?s skos:exactMatch ?ysac .
    FILTER(STRSTARTS(STR(?ysac), 'http://www.yso.fi/onto/ysa/'))
    ?ysac skos:closeMatch ?place .
    ?s skos:prefLabel ?label .
    FILTER(LANG(?label)='fi')
  }
  GRAPH <http://ldf.fi/pnr/> {
    ?place a ?placetype .
    ?placetype rdfs:label ?typelabel .
    FILTER(LANG(?typelabel)='fi')
    ?place geo:lat ?lat .
    ?place geo:long ?long .
  }
} 
#LIMIT 10
"""

sparql = SPARQLWrapper.SPARQLWrapper2(endpoint)
sparql.setQuery(QUERY)
results = sparql.query()

kml = KML.kml()
doc = KML.Document()
kml.append(doc)

for binding in results.bindings:
    doc.append(KML.Placemark(
        KML.name(binding['label'].value),
        KML.description(binding['place'].value + "\n" + binding['typelabel'].value),
        KML.Point(
            KML.coordinates('%s,%s' % (binding['long'].value, binding['lat'].value))
        )
    ))

print etree.tostring(etree.ElementTree(kml),pretty_print=True)
