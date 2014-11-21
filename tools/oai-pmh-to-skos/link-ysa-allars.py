#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
import sys

if len(sys.argv) != 6:
    print >>sys.stderr, "Usage: %s <ysa.ttl> <allars.ttl> <yso.ttl> <ysa-linked.ttl> <allars-linked.ttl>" % sys.argv[0]
    sys.exit(1)

ysa = Graph()
ysa.parse(sys.argv[1], format='turtle')

allars = Graph()
allars.parse(sys.argv[2], format='turtle')

OWL=Namespace("http://www.w3.org/2002/07/owl#")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
YSA=Namespace("http://www.yso.fi/onto/ysa/")
ALLARS=Namespace("http://www.yso.fi/onto/allars/")

# figure out the equivalences
ysa_to_allars = {}
allars_to_ysa = {}

def find_labels(voc, conc, lang):
    labels = voc.preferredLabel(conc, lang=lang)
    return [l[1] for l in labels] # ignore property information

def find_links(src, dst, conc, lang):
    labels = find_labels(src, conc, lang)
    all_dconcs = []
    for label in labels:
#        print conc, label
        dconcs = list(dst.subjects(SKOS.prefLabel, label))
        if len(dconcs) == 0:
            dconcs = list(dst.subjects(SKOS.altLabel, label))
            if len(dconcs) > 0:
                for dconc in dconcs:
                    preflabel = find_labels(dst, dconc, lang)[0]
                    print >>sys.stderr, ("%s linked via altLabel '%s' to %s, should be '%s'" % (conc, label, dconc, preflabel)).encode('UTF-8')
            else:
                print >>sys.stderr, ("%s equivalent term '%s' not found" % (conc, label)).encode('UTF-8')
#        for dconc in dconcs:
#            print " -> ", dconc
        all_dconcs += dconcs
    return all_dconcs

for aconc in allars.subjects(RDF.type, SKOS.Concept):
    yconcs = find_links(allars, ysa, aconc, 'fi')
    for yconc in yconcs:
        ysa_to_allars.setdefault(yconc, [])
        ysa_to_allars[yconc].append(aconc)
        allars_to_ysa.setdefault(aconc, [])
        allars_to_ysa[aconc].append(yconc)

# remove Finnish data from Allars
for s,p,o in allars.triples((None,None,None)):
    if isinstance(o, Literal) and o.language == 'fi':
        allars.remove((s,p,o))

# link YSA to Allars and vice versa
for ysaconc, allarsconcs in ysa_to_allars.items():
    if len(allarsconcs) == 1:
        allarsconc = allarsconcs[0]
        if len(allars_to_ysa[allarsconc]) == 1:
            ysa.add((ysaconc, SKOS.exactMatch, allarsconc))
            allars.add((allarsconc, SKOS.exactMatch, ysaconc))
        else:
            ysa.add((ysaconc, SKOS.broadMatch, allarsconc))
            allars.add((allarsconc, SKOS.narrowMatch, ysaconc))
    else:
        for allarsconc in allarsconcs:
            if len(allars_to_ysa[allarsconc]) != 1:
                print >>sys.stderr, "Inconsistent mappings: %s -> %s -> %s" % (ysaconc, allarsconc, str(allars_to_ysa[allarsconc]))
            ysa.add((ysaconc, SKOS.narrowMatch, allarsconc))
            allars.add((allarsconc, SKOS.broadMatch, ysaconc))

# add links to YSO
yso = Graph()
yso.parse(sys.argv[3], format='turtle')

for s,o in yso.subject_objects(SKOS.closeMatch):
    if (s, OWL.deprecated, Literal('true', datatype=XSD.boolean)) in yso:
        continue # ignore deprecated YSO concepts
    if o.startswith(YSA):
        if (o, RDF.type, SKOS.Concept) in ysa:
            ysa.add((o, SKOS.closeMatch, s))
        else:
            print >>sys.stderr, "YSO concept %s linked to nonexistent YSA concept %s" % (s,o)
    elif o.startswith(ALLARS):
        if (o, RDF.type, SKOS.Concept) in allars:
            allars.add((o, SKOS.closeMatch, s))
        else:
            print >>sys.stderr, "YSO concept %s linked to nonexistent Allars concept %s" % (s,o)

ysaout = open(sys.argv[4], 'w')
ysa.serialize(destination=ysaout, format='turtle')
ysaout.close()

allarsout = open(sys.argv[5], 'w')
allars.serialize(destination=allarsout, format='turtle')
allarsout.close()
