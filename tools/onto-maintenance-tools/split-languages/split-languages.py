#!/usr/bin/env python

from rdflib import *
import os
import time
import sys


def convert_lang_tags(graph, lang):

    # Looping through the literals in the specified language
    for s, p, o in list(g):


        if isinstance(o, Literal) and o.language == lang:

            orig_uri = str(p)
            new_uri = orig_uri + '_' + lang.upper()

            # Removes the lang tag and moving the literal value to
            # the property originalPropertyURI_LANG
            new_prop = URIRef(new_uri)

            old_triple = (s, p, o)
            new_triple = (s, new_prop, o)

            graph.remove(old_triple)
            graph.add(new_triple)

            # Adding that the new property is an annotation property
            graph.add((new_prop, RDF.type, RDF.Property))
            graph.add((new_prop, RDF.type, OWL.AnnotationProperty))



onto_path = sys.argv[1]
out_put_path = sys.argv[2]


# print(time.strftime("%H:%M:%S"))

g = Graph()
g.parse(onto_path, format='n3')


# print(time.strftime("%H:%M:%S"))


# Converts the Swedish language tags
lang = 'sv'
convert_lang_tags(g, lang)

# Converts the English language tags
lang = 'en'
convert_lang_tags(g, lang)


# print(time.strftime("%H:%M:%S"))

g.serialize(out_put_path, format='turtle')

# print('Ended')
# print(time.strftime("%H:%M:%S"))


