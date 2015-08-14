#!/usr/bin/env python

from rdflib import Graph, Namespace, RDF
import requests
import sys
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

concepts = sorted(g.subjects(SKOS.inScheme, YSO['']))

writer = csv.writer(sys.stdout)

stats = {} # key: lang, val: dict with keys 'pref' and 'alt'

def concept_singulars(conc):
    vals = [conc]
    for lang in PLURAL_SUFFIXES.keys():
        stats.setdefault(lang, {})
        try:
            prefLabel = g.preferredLabel(conc, lang=lang)[0][1]
            labelSingular, must_check = singular(unicode(prefLabel), lang)
            if labelSingular.lower() == prefLabel.lower():
                labelSingular = '' # did not change
            stats[lang].setdefault('pref', 0)
            stats[lang]['pref'] += 1
        except:
            prefLabel = labelSingular = ''
            must_check = set()
        vals += [prefLabel, labelSingular, ', '.join(must_check)]
    rows = [vals]
    # base forms for altLabels
    alt_baseforms = {} # key: lang, val: list of tuples (label, baseform, must_check))
    for altLabel in g.objects(conc, SKOS.altLabel):
        label = unicode(altLabel)
        lang = altLabel.language
        alt_baseforms.setdefault(lang, [])
        labelSingular, must_check = singular(label, lang)
        if labelSingular.lower() == label.lower():
            labelSingular = '' # did not change
        result = (label, labelSingular, ', '.join(must_check))
        alt_baseforms[lang].append(result)
    if len(alt_baseforms) > 0:
        max_altlabels = max([len(v) for lang,v in alt_baseforms.items()])
        for i in range(max_altlabels):
            vals = ['']
            for lang in PLURAL_SUFFIXES.keys():
                try:
                    result = alt_baseforms[lang][i]
                    stats[lang].setdefault('alt', 0)
                    stats[lang]['alt'] += 1
                except:
                    result = ('','','')
                vals += result
            rows.append(vals)
    return rows

for conc in concepts:
    is_plural = False
    for lang,pl_suffix in PLURAL_SUFFIXES.items():
        try:
            label = g.preferredLabel(conc, lang=lang)[0][1]
            if label.endswith(pl_suffix):
                is_plural = True
        except:
            pass
    if not is_plural:
        continue
    rows = concept_singulars(conc)
    for row in rows:
        writer.writerow([s.encode('UTF-8') for s in row])

for lang, vals in stats.items():
    print >>sys.stderr, "%s: %d preferred, %d alternate" % (lang, vals['pref'], vals['alt'])
