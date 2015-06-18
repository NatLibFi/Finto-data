#!/usr/bin/env python

from rdflib import Graph, Namespace, RDF
import requests
import sys
import random
import csv

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
YSO = Namespace("http://www.yso.fi/onto/yso/")

APIBASE="http://demo.seco.tkk.fi/las/"
PLURAL_SUFFIXES = {'fi': 't', 'sv': 'r', 'en': 's'}

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

concepts = list(g.subjects(SKOS.inScheme, YSO['']))
random.shuffle(concepts)

writer = csv.writer(sys.stdout)
i = 0

for conc in concepts:
    vals = [conc]
    is_plural = False
    for lang,pl_suffix in PLURAL_SUFFIXES.items():
        try:
            label = g.preferredLabel(conc, lang=lang)[0][1]
            if label.endswith(pl_suffix):
                is_plural = True
            labelSingular = singular(label, lang)
        except:
            label = labelSingular = ''
        vals += [label.encode('UTF-8'), labelSingular.encode('UTF-8')]
    if not is_plural:
        continue
    writer.writerow(vals)
    i += 1
    if i >= 1000: break
