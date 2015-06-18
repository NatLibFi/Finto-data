#!/usr/bin/env python

from rdflib import Graph, Namespace, RDF
import requests
import sys
import random
import csv

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
YSO = Namespace("http://www.yso.fi/onto/yso/")

APIBASE="http://demo.seco.tkk.fi/las/"
LANGUAGES=('fi', 'sv', 'en')

def singular(label, lang):
    url = APIBASE + "baseform"
    params = {'locale': lang, 'text': label}
    r = requests.get(url, params=params)
    result = r.json()
    if label.lower() == result.lower():
        return '' # no difference
    else:
        return result

g = Graph()
g.parse(sys.argv[1], format='turtle')

concepts = set(g.subjects(SKOS.inScheme, YSO['']))
sample = random.sample(concepts, 1000)

writer = csv.writer(sys.stdout)


for conc in sample:
    vals = [conc]
    for lang in LANGUAGES:
        try:
            label = g.preferredLabel(conc, lang=lang)[0][1]
            labelSingular = singular(label, lang)
        except:
            label = labelSingular = ''
        vals += [label.encode('UTF-8'), labelSingular.encode('UTF-8')]
    writer.writerow(vals)
        
