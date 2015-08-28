#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#LIMIT 100
"""

sparql = SPARQLWrapper.SPARQLWrapper2(endpoint)
sparql.setQuery(QUERY)
results = sparql.query()

kml = KML.kml()
doc = KML.Document()
kml.append(doc)

STYLES = (
  # Kulkuväylä
  (110, 'http://maps.google.com/mapfiles/kml/shapes/cabs.png'),
  # Rautatieliikennepaikka
  (120, 'http://maps.google.com/mapfiles/kml/shapes/rail.png'),
  # Urheilu- tai virkistysalue
  (245, 'http://maps.google.com/mapfiles/kml/shapes/parks.png'),
  # Metsäalue
  (325, 'http://maps.google.com/mapfiles/kml/shapes/parks.png'),
  # Suo
  (330, 'http://maps.google.com/mapfiles/kml/shapes/parks.png'),
  # Saari
  (335, 'http://maps.google.com/mapfiles/kml/shapes/mountains.png'),
  # Niemi
  (345, 'http://maps.google.com/mapfiles/kml/shapes/target.png'),
  # Saari
  (350, 'http://maps.google.com/mapfiles/kml/shapes/target.png'),
  # Muu maastokohde
  (390, 'http://maps.google.com/mapfiles/kml/shapes/target.png'),
  # Vakavesi
  (410, 'http://maps.google.com/mapfiles/kml/shapes/water.png'),
  # Vakaveden osa
  (415, 'http://maps.google.com/mapfiles/kml/shapes/water.png'),
  # Virtavesi
  (420, 'http://maps.google.com/mapfiles/kml/shapes/water.png'),
  # Virtaveden osa
  (425, 'http://maps.google.com/mapfiles/kml/shapes/water.png'),
  # Koski
  (435, 'http://maps.google.com/mapfiles/kml/shapes/water.png'),
  # Kunta, kaupunki
  (540, 'http://maps.google.com/mapfiles/kml/shapes/ranger_station.png'),
  # Kunta, maaseutu
  (550, 'http://maps.google.com/mapfiles/kml/shapes/ranger_station.png'),
  # Kylä, kaupunginosa tai kulmakunta
  (560, 'http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png', 0.7),
  # Talo
  (570, 'http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png', 0.7),
  # Maakunta
  (575, 'http://maps.google.com/mapfiles/kml/shapes/schools.png', 1.2),
  # Lääni
  (580, 'http://maps.google.com/mapfiles/kml/shapes/schools.png', 1.2),
  # Erämaa-alue
  (630, 'http://maps.google.com/mapfiles/kml/shapes/parks.png'),
)

for styledef in STYLES:
    styleid = str(styledef[0])
    iconurl = styledef[1]
    if len(styledef) > 2:
        scale = str(styledef[2])
    else:
        scale = str(1.0)
    doc.append(
        KML.Style(
            KML.IconStyle(
                KML.Icon(
                    KML.href(iconurl),
                    KML.scale(scale)
                )
            ),
            id=str(styleid)
        )
    )
            

for binding in results.bindings:
    doc.append(KML.Placemark(
        KML.name(binding['label'].value),
        KML.description(binding['place'].value + "\n" + binding['typelabel'].value),
        KML.styleUrl('#' + binding['placetype'].value[-3:]),
        KML.Point(
            KML.coordinates('%s,%s' % (binding['long'].value, binding['lat'].value))
        )
    ))

print etree.tostring(etree.ElementTree(kml),pretty_print=True)
