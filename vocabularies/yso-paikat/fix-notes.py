#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Literal
from rdflib.namespace import SKOS
import sys
import re

g = Graph()
g.parse(sys.argv[1], format='turtle')

substitutions = {}
regex_by_lang = {}

for place, oldLabel in g.subject_objects(SKOS.hiddenLabel):
    lang = oldLabel.language
    substitutions.setdefault(lang, {})
    newLabel = g.preferredLabel(place, lang=lang)[0][1]
    if oldLabel == newLabel:
        continue # no need to substitute since labels didn't change
    if oldLabel in substitutions[lang]:
        print >>sys.stderr, "Warning: '%s' is ambiguous, '%s' or '%s'" % (oldLabel, substitutions[lang][oldLabel], newLabel)
    substitutions[lang][unicode(oldLabel)] = unicode(newLabel)

for lang in substitutions.keys():
    subst_keys = substitutions[lang].keys()
    subst_keys.sort(key=lambda i:len(i), reverse=True)
    # build language-specific regexes from the substitutions
    regex_by_lang[lang] = re.compile(r"\b(%s)\b" % "|".join(map(re.escape, subst_keys)), re.UNICODE)

for place, note in g.subject_objects(SKOS.note):
    lang = note.language
    newnote = regex_by_lang[lang].sub(lambda mo: substitutions[lang][mo.group(1)], note)
    if unicode(note) != newnote:
        g.remove((place, SKOS.note, note))
        g.add((place, SKOS.note, Literal(newnote, lang)))

# remove hiddenLabels
for place, hlabel in g.subject_objects(SKOS.hiddenLabel):
    g.remove((place, SKOS.hiddenLabel, hlabel))

# serialize the graph
g.serialize(destination=sys.stdout, format='turtle')
