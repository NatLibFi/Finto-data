#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys
import re

old_filenames = {'palveluluokat-fi.csv': 'palveluluokat-fi.ttl','palveluluokat-en.csv': 'palveluluokat-en.ttl','palveluluokat-sv.csv': 'palveluluokat-sv.ttl', 'kohderyhmat-fi.csv': 'kohderyhmat-fi.ttl', 'kohderyhmat-en.csv': 'kohderyhmat-en.ttl', 'kohderyhmat-sv.csv': 'kohderyhmat-sv.ttl','elamantilanteet-fi.csv': 'elamantilanteet-fi.ttl', 'elamantilanteet-en.csv': 'elamantilanteet-en.ttl','elamantilanteet-sv.csv': 'elamantilanteet-sv.ttl', 'tuottajatyypit-fi.csv': 'tuottajatyypit-fi.ttl', 'tuottajatyypit-en.csv': 'tuottajatyypit-en.ttl', 'tuottajatyypit-sv.csv': 'tuottajatyypit-sv.ttl','toteutustavat-fi.csv': 'toteutustavat-fi.ttl','toteutustavat-en.csv': 'toteutustavat-en.ttl','toteutustavat-sv.csv': 'toteutustavat-sv.ttl'}

filenames = {'palveluluokat.csv': 'palveluluokat.ttl', 'kohderyhmat.csv': 'kohderyhmat.ttl', 'elamantilanteet.csv': 'elamantilanteet.ttl', 'tuottajatyypit.csv': 'tuottajatyypit.ttl', 'tuotantotavat.csv': 'tuotantotavat.ttl'}

PTVL = Namespace("http://urn.fi/URN:NBN:fi:au:ptvl:")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('ptvl', PTVL)

def add_concept(row):
    cid = row[0].strip()
    notation = row[1].replace(' ','')
    if (notation.endswith('.')):
        notation = notation[:-1]
    prefFi = row[2].strip()
    prefSv = row[3].strip()
    prefEn = row[4].strip()
    noteFi = row[5].strip()
    noteSv = row[6].strip()
    noteEn = row[7].strip()
    uri = PTVL[cid]
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.notation, Literal(notation)))
    if len(prefFi) > 0:
        g.add((uri, SKOS.prefLabel, Literal(prefFi, 'fi')))
    if len(prefSv) > 0:
        g.add((uri, SKOS.prefLabel, Literal(prefSv, 'sv')))
    if len(prefEn) > 0:
        g.add((uri, SKOS.prefLabel, Literal(prefEn, 'en')))
    if len(noteFi) > 0:
        g.add((uri, SKOS.note, Literal(noteFi, 'fi')))
    if len(noteSv) > 0:
        g.add((uri, SKOS.note, Literal(noteSv, 'sv')))
    if len(noteEn) > 0:
        g.add((uri, SKOS.note, Literal(noteEn, 'en')))
    m = re.search('^\D+', notation)
    schemeid = m.group(0).strip()
    if schemeid != 'P':
        schemeuri = URIRef("http://urn.fi/URN:NBN:fi:au:ptvl:" + schemeid)
    else:
        schemeuri = URIRef("http://urn.fi/URN:NBN:fi:au:ptvl:")
    g.add((uri, SKOS.inScheme, schemeuri))

    
def add_broader(row):
    cid = row[0].strip()
    notation = row[1].strip()
    if (notation.endswith('.')):
        notation = notation[:-1]
    if '.' in notation:
        for broaderuri in g.subjects(SKOS.notation, Literal(notation.rsplit('.', 1)[0])):
            g.add((URIRef("http://urn.fi/URN:NBN:fi:au:ptvl:" + cid), SKOS.broader, broaderuri))

def hasNumbers(string):
    return bool(re.search(r'\d', string))

for csvfile in filenames:
    with open(csvfile, 'rb') as cf:
        reader = csv.reader(cf)
        next(reader, None) # skip the header row
        for row in reader:
            add_concept(row)
        cf.seek(0)
        next(reader, None)
        for row in reader:
            add_broader(row)

g.serialize(destination='ptvl.ttl', format='turtle')
