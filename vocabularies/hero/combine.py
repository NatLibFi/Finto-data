#!/usr/bin/env python

import rdflib, sys
from rdflib import Graph, RDF, XSD, URIRef, plugin, Literal, Namespace
import unicodecsv as csv
from io import BytesIO

skos = Namespace("http://www.w3.org/2004/02/skos/core#")
herometa = Namespace("http://www.yso.fi/onto/hero-meta/")

hero = Graph().parse('hero.ttl', format='turtle')
csvfile = open('HERO.csv', 'rb')
reader = csv.reader(csvfile, encoding='utf-8', delimiter=';')
types = ['', herometa.UpperConcept, herometa.NonHeraldicConcept, herometa.NonFinnishConcept]
langcodes = ['fi', 'et', 'hu', 'en', 'nl', 'de', 'sv', 'nb', 'nn', 'da', 'is', 'lt', 'lv', 'sq', 'el', 'la', 'it', 'fr', 'es', 'ca', 'pt', 'ro', 'pl', 'cs', 'sk', 'sl', 'hr', 'sr', 'bg', 'ru', 'be', 'uk']
wbo_missing = False

for row in reader:
    heroid = row[0]
    wbo = row[-1]
    if not wbo.isalnum():
        wbo_missing = True
        wbo = ''
    uri = URIRef('http://www.yso.fi/onto/hero/p' + heroid)
    if (uri, None, None) not in hero:
        print 'MISSING: ' + heroid 
    if len(wbo) > 0:
        hero.add( (uri, herometa.wboMatch, Literal(wbo)) )
    end = -1
    if wbo_missing:
        end = None 
    for index, label in enumerate(row[1:end]):
        #print "{} / {}".format(index, len(row))
        if " {" in label:
            labstr = label.split(" {")
            if len(labstr) > 1:
                pref = labstr[0]
                lablang = labstr[1][1:3]
                if lablang == 'fi':
                    hero.remove((uri, skos.prefLabel, None))
                hero.add( (uri, skos.prefLabel, Literal(pref, lang=lablang)) )
        elif len(label) > 0 and index == len(row)-2: #handle the wikidata uris
            wikidatauri = "http://wikidata.org/wiki/" + label
            hero.add((uri, skos.relatedMatch, URIRef(wikidatauri)))
        elif len(label) > 0:
            lablang = langcodes[index]
            hero.add((uri, skos.prefLabel, Literal(label, lang=lablang)))
        if len(label) == 0 and index == 0: # remove false finnish preflabel
            hero.remove((uri, skos.prefLabel, None))
            
hero.serialize(destination='hero-combined.ttl', format='turtle')
