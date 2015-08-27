#!/usr/bin/env python

import sys
import csv
import urllib2
from rdflib import Graph, URIRef, Literal, Namespace

DOCID='1-bryYIkkP2vd7Vgcf2IAOAr5azZpDRjcBJaEPYG3xcc'

csvurl='https://docs.google.com/spreadsheets/d/%s/export?format=csv' % DOCID

data = urllib2.urlopen(csvurl)
reader = csv.reader(data)

g = Graph()
PNR = Namespace('http://ldf.fi/pnr/')
YSA = Namespace('http://www.yso.fi/onto/ysa/')
YSAMETA = Namespace('http://www.yso.fi/onto/ysa-meta/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

g.namespace_manager.bind('pnr', PNR)
g.namespace_manager.bind('ysa', YSA)
g.namespace_manager.bind('ysameta', YSAMETA)
g.namespace_manager.bind('skos', SKOS)

rowidx = 0
for row in reader:
    rowidx += 1
    if rowidx == 1:
        continue # skip header
    ysac = URIRef(row[0].strip())
    result = row[6].strip()
    comments = row[7].strip().decode('UTF-8')
    if row[8].strip() != '':
        place = URIRef(row[8].strip())
    else:
        place = None
    
    if comments != '':
        g.add((ysac, SKOS.editorialNote, Literal(comments, 'fi')))
    
    if result.upper() == 'U':
        g.add((ysac, YSAMETA.isForeign, Literal(True)))
        continue
    
    if result == '1':
        if place is not None:
            g.add((ysac, SKOS.closeMatch, place))
        else:
            print >>sys.stderr, "ERROR on row %d: result=1 with no place" % rowidx
        continue
    
    if result == '0':
        if place is not None:
            g.add((ysac, YSAMETA.nonMatch, place))
        continue
    
    if result == '?' or result == '':
        continue
    
    for placeid in result.split():
        place = PNR[placeid]
        g.add((ysac, SKOS.closeMatch, place))

g.serialize(destination=sys.stdout, format='turtle')
