#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
import sys

musa = Graph()
musa.parse(sys.argv[1], format='turtle')

cilla = Graph()
cilla.parse(sys.argv[2], format='turtle')

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
DCT=Namespace("http://purl.org/dc/terms/")
CILLA=Namespace("http://www.yso.fi/onto/cilla/")

# figure out the equivalences
cilla_to_musa = {}

def find_label(voc, conc, lang):
    labels = voc.preferredLabel(conc, lang=lang)
    if len(labels) != 0:
        return labels[0][1]
    return None

def find_link(src, dst, conc, lang):
    label = find_label(src, conc, lang)
    dconc = dst.value(None, SKOS.prefLabel, label)
    if dconc is None:
        dconc = dst.value(None, SKOS.altLabel, label)
    return dconc

for mconc in musa.subjects(RDF.type, SKOS.Concept):
    for linklang in ['sv','fi']:
        cconc = find_link(musa, cilla, mconc, linklang)
        if cconc is not None:
            cilla_to_musa[cconc] = mconc
            break

for cconc in cilla.subjects(RDF.type, SKOS.Concept):
    if cconc in cilla_to_musa: continue # already linked
    for linklang in ['sv','fi']:
        mconc = find_link(cilla, musa, cconc, linklang)
        if mconc is not None:
            cilla_to_musa[cconc] = mconc
            break

# remove Swedish data from MUSA
for s,p,o in musa.triples((None,None,None)):
    if isinstance(o, Literal) and o.language == 'sv':
        musa.remove((s,p,o))

# merge Cilla data to MUSA
for cconc in cilla.subjects(RDF.type, SKOS.Concept):
    mconc = cilla_to_musa.get(cconc, None)
    if mconc is None:
        print >>sys.stderr, ("No MUSA concept found for CILLA concept %s '%s'" % (cconc, find_label(cilla, cconc, 'sv'))).encode('UTF-8')
        continue

    for p,o in cilla.predicate_objects(cconc):
        if o.startswith(CILLA):
            if o in cilla_to_musa:
                o = cilla_to_musa[o]
            else:
                continue
        if isinstance(o, Literal) and o.language == 'fi':
            continue

        if p == DCT.created:
            musats = musa.value(mconc, p, None)
            if musats > o:
                musa.remove((mconc, p, musats))
                # use the older timestamp from CILLA instead
            else:
                continue # use the timestamp from MUSA, forget this CILLA ts

        if p == DCT.modified:
            musats = musa.value(mconc, p, None)
            if musats < o:
                musa.remove((mconc, p, musats))
                # use the newer timestamp from CILLA instead
            else:
                continue # use the timestamp from MUSA, forget this CILLA ts

        musa.add((mconc, p, o))

musa.serialize(destination=sys.stdout, format='turtle')
