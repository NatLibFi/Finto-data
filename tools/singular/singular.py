#!/usr/bin/env python

from rdflib import Graph, Namespace, RDF
import requests
import sys
import random
import csv
import re

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
YSO = Namespace("http://www.yso.fi/onto/yso/")

APIBASE="http://demo.seco.tkk.fi/las/"
PLURAL_SUFFIXES = {'fi': 't', 'sv': 'r', 'en': 's'}

def singular(label, lang):
    # check for qualifiers in parentheses and avoid processing those
    m = re.match(r'(.*)( \(.*\))', label)
    if m is not None:
        result, must_check = singular(m.group(1), lang)
        return (result + m.group(2), must_check)

    # check for chained terms and process each part separately
    m = re.match(r'(.*) -- (.*)', label)
    if m is not None:
        result1, must_check1 = singular(m.group(1), lang)
        result2, must_check2 = singular(m.group(2), lang)
        return (result1 + " -- " + result2, must_check1 | must_check2)
    
    must_check = set()
    url = APIBASE + "baseform"
    params = {'locale': lang, 'text': label}
    r = requests.get(url, params=params)
    result = r.json()
    if lang == 'en' and ' of ' in label: # fix 'X of Y' turning to 'X have Y' in English
        result = result.replace(' have ', ' of ')
    # check for likely problem cases
    if '-' in label:
        must_check.add('viiva')
    if '-' in result:
        must_check.add('viiva')
    if ',' in label:
        must_check.add('pilkku')
    if label.lower() != label:
        must_check.add('isokirjain')
    if '(' in label and '(' not in result:
        must_check.add('sulut')
    if lang == 'fi' and re.search(r'inen\w', result):
        must_check.add('inen')
    return (result, must_check)

g = Graph()
g.parse(sys.argv[1], format='turtle')

concepts = list(g.subjects(SKOS.inScheme, YSO['']))
random.seed(0)
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
            labelSingular, must_check = singular(unicode(label), lang)
            if labelSingular.lower() == label.lower():
                labelSingular = '' # did not change
        except:
            label = labelSingular = ''
            must_check = set()
        vals += [label.encode('UTF-8'), labelSingular.encode('UTF-8'), ', '.join(must_check).encode('UTF-8')]
    if not is_plural:
        continue
    writer.writerow(vals)
    i += 1
    if i >= 1000: break
