#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys
import re

filenames = {'palveluluokat-fi.csv': 'palveluluokat-fi.ttl','palveluluokat-en.csv': 'palveluluokat-en.ttl','palveluluokat-sv.csv': 'palveluluokat-sv.ttl', 'kohderyhmat-fi.csv': 'kohderyhmat-fi.ttl', 'kohderyhmat-en.csv': 'kohderyhmat-en.ttl', 'kohderyhmat-sv.csv': 'kohderyhmat-sv.ttl','elamantilanteet-fi.csv': 'elamantilanteet-fi.ttl', 'elamantilanteet-en.csv': 'elamantilanteet-en.ttl','elamantilanteet-sv.csv': 'elamantilanteet-sv.ttl', 'tuottajatyypit-fi.csv': 'tuottajatyypit-fi.ttl', 'tuottajatyypit-en.csv': 'tuottajatyypit-en.ttl', 'tuottajatyypit-sv.csv': 'tuottajatyypit-sv.ttl','toteutustavat-fi.csv': 'toteutustavat-fi.ttl','toteutustavat-en.csv': 'toteutustavat-en.ttl','toteutustavat-sv.csv': 'toteutustavat-sv.ttl'}

PTVL = Namespace("http://urn.fi/URN:NBN:fi:au:ptvl:")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('ptvl', PTVL)

uris = []

def get_uri(cell):
    notation, label = cell.split(" ", 1)
    if (notation.endswith('.')):
        notation = notation[:-1]
    return PTVL[notation]

def add_concept(cell):
    notation, label = cell.split(" ", 1)
    if (notation.endswith('.')):
        notation = notation[:-1]
    uri = PTVL[notation]
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.notation, Literal(notation)))
    g.add((uri, SKOS.prefLabel, Literal(label, language)))
    m = re.search('^\D+', notation)
    schemeid = m.group(0)
    if schemeid != 'P':
        schemeuri = PTVL[schemeid]
    else:
        schemeuri = PTVL['']
    g.add((uri, SKOS.inScheme, schemeuri))

    if '.' in notation:
        parent = notation.rsplit('.', 1)[0]
        parenturi = PTVL[parent]
        g.add((uri, SKOS.broader, parenturi))
        g.add((parenturi, SKOS.narrower, uri))
    else:
        g.add((uri, SKOS.topConceptOf, schemeuri))
        g.add((schemeuri, SKOS.hasTopConcept, uri))

def add_description(cell, uri, language):
    g.add((uri, SKOS.note, Literal(cell, lang=language)))

def hasNumbers(string):
    return bool(re.search(r'\d', string))

for csvfile in filenames:
    language = csvfile[-6:-4]
    with open(csvfile, 'rb') as cf:
        reader = csv.reader(cf)
        prev_row = []
        for row in reader:
            cell_num = 0
            for cell in row:
                if cell.strip() != '':
                    if hasNumbers(cell[0:5]):
                        add_concept(cell.strip())
                    else:
                        lang = csvfile.split("-")[1].replace('.csv', '') 
                        add_description(cell.strip(), get_uri(prev_row[cell_num]), lang)
                cell_num += 1 
            prev_row = row

g.serialize(destination='ptvl.ttl', format='turtle')
