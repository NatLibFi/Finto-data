#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Literal
from rdflib.namespace import SKOS, DC
import sys

TYPEMAP = {
  u'vakavesi' : { 'fi': u'järvi', 'sv': u'sjö'},
  u'kylä, kaupunginosa tai kulmakunta' : { 'fi': u'kylä', 'sv': u'by'}
}


def get_place_type(g, place, lang):
    src = g.value(place, DC.source, None)
    if src is None:
        return None
    pnrtype = src.split('tyyppitieto: ')[1]
    return TYPEMAP[pnrtype.lower()][lang]

g = Graph()
g.parse(sys.argv[1], format='turtle')

by_label = {}
for place, label in g.subject_objects(SKOS.prefLabel):
    by_label.setdefault(label, [])
    by_label[label].append(place)

ambiguous = [(label, places) for label, places in by_label.items() if len(places)>1]

for label, places in sorted(ambiguous):
    lang = label.language
    print >>sys.stderr, "Disambiguating:", label, "lang:", lang, "places:", ' '.join(places)
    for place in places:
        type = get_place_type(g, place, lang)
        if type is None:
            print >>sys.stderr, "-- cannot disambiguate %s" % place
            continue
        newlabel = Literal(u"%s : %s)" % (label[:-1], type), lang)
        print >>sys.stderr, "-- new label for %s: %s" % (place, newlabel)
        g.remove((place, SKOS.prefLabel, label))
        g.add((place, SKOS.prefLabel, newlabel))

g.serialize(destination=sys.stdout, format='turtle')
