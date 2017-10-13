#!/usr/bin/env python

# Expand references to concept URIs to HTML links with concept labels
# in scope notes and definitions. Write the modified vocabulary on stdout.

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS
import re
import sys

inputfile = sys.argv[1]

g = Graph()
g.parse(inputfile, format='turtle')

URIRE = re.compile(r'\[(http://www.yso.fi/onto/[a-z]+/p[0-9]+)\]')

def uri_to_link(lang, matchobj):
    uri = matchobj.group(1)
    concept = URIRef(uri)
    labels = g.preferredLabel(concept, lang)
    try:
        label = labels[0][1]
    except IndexError:
        return matchobj.group(0) # don't change if we can't find a label
    return "<a href='%s'>%s</a>" % (uri, label)
    


NOTEPROPS = (SKOS.note, SKOS.scopeNote, SKOS.definition)
for prop in NOTEPROPS:
    for s,o in g.subject_objects(prop):
        lang = o.language
        if URIRE.search(o) is not None:
            new = URIRE.sub(lambda m:uri_to_link(lang, m), o)
            g.remove((s, prop, o))
            g.add((s, prop, Literal(new, lang)))
            

g.serialize(destination=sys.stdout, format='turtle')
