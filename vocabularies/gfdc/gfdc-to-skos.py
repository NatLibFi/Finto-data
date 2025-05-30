#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
import csv
import sys
import re

if len(sys.argv) != 4:
    print >>sys.stderr, "Usage: %s <classes.csv> <glossary.csv> <metadata.csv>" % sys.argv[0]
    sys.exit(1)

classes_file = sys.argv[1]
glossary_file = sys.argv[2]
metadata_file = sys.argv[3]

DC = Namespace("http://purl.org/dc/elements/1.1/")
GFDC = Namespace("http://urn.fi/URN:NBN:fi:au:gfdc:")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# map 3-letter ISO 639-2 language codes to 2-letter 639-1 codes used in RDF
LANGMAP = {
    'eng': 'en',
    'fin': 'fi',
    'swe': 'sv',
    'ger': 'de',
    'fre': 'fr',
    'slv': 'sl'
}

g = Graph()
g.namespace_manager.bind('dc', DC)
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('gfdc', GFDC)

def class_uri(notation):
    return GFDC['C' + notation.replace(' ','')]

def concept_uri(conceptid):
    return GFDC['G%04d' % int(conceptid)]

def cleanup_note(note):
    note = note.strip()
    if note.startswith('[') or note.startswith('('):
        note = note[1:]
    if note.endswith(']') or note.endswith(')'):
        note = note[:-1]
    return note.strip()

def add_class(notation, labels, includingNotes, scopeNotes, BT, seeAlsos):
    uri = class_uri(notation)
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, RDF.type, GFDC.Class))
    g.add((uri, SKOS.notation, Literal(notation)))
    for lang3, lang2 in LANGMAP.items():
        if labels[lang3] != '' and labels[lang3] != 'MISSING_VALUE':
            g.add((uri, SKOS.prefLabel, Literal(labels[lang3], lang2)))
        if includingNotes[lang3] != '':
            g.add((uri, SKOS.scopeNote, Literal(cleanup_note(includingNotes[lang3]), lang2)))
        if scopeNotes[lang3] != '':
            g.add((uri, SKOS.scopeNote, Literal(cleanup_note(scopeNotes[lang3]), lang2)))
    for seeAlso in seeAlsos:
        if ' ' in seeAlso:
            print >>sys.stderr, "Skipping bad seeAlso value '%s'" % seeAlso
            continue
        if seeAlso == '':
            continue
        other = class_uri(seeAlso)
        g.add((uri, SKOS.related, other))
        g.add((other, SKOS.related, uri))
    
    if BT != '':
        g.add((uri, SKOS.broader, class_uri(BT)))
        g.add((class_uri(BT), SKOS.narrower, uri))
    else:
        g.add((uri, SKOS.topConceptOf, GFDC['']))
        g.add((GFDC[''], SKOS.hasTopConcept, uri))
    g.add((uri, SKOS.inScheme, GFDC['']))

def add_concept(conceptid, clnum, labels, altLabels, hiddenLabels):
    uri = concept_uri(conceptid)
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, RDF.type, GFDC.GlossaryConcept))
    for lang, label in labels.items():
        if labels[lang] != '':
            g.add((uri, SKOS.prefLabel, Literal(labels[lang], lang)))
    for lang, altlabels in altLabels.items():
        for altlabel in altlabels:
            if altlabel != '':
                g.add((uri, SKOS.altLabel, Literal(altlabel, lang)))
    for lang, hiddenlabels in hiddenLabels.items():
        for hiddenlabel in hiddenlabels:
            if hiddenlabel != '':
                g.add((uri, SKOS.hiddenLabel, Literal(hiddenlabel, lang)))
    
    # link to class
    cluri = class_uri(clnum)
    g.add((uri, SKOS.relatedMatch, cluri))
    g.add((cluri, SKOS.relatedMatch, uri))
    g.add((uri, SKOS.inScheme, GFDC['G']))

def add_metadata(field, values):
    prefix, ln = field.split(':')
    namespaces = dict(g.namespace_manager.namespaces())
    ns = namespaces[prefix]
    fielduri = URIRef(ns + ln)
    for lang3, lang2 in LANGMAP.items():
        if values[lang3] != '':
            for val in values[lang3].splitlines():
                if val == '':
                    continue
                g.add((GFDC[''], fielduri, Literal(val, lang2)))

with open(classes_file, 'rb') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        labels = {}
        includingNotes = {}
        scopeNotes = {}
        BT = row['BT']
        seeAlsos = row['seeAlso'].split('|')
        for lang in LANGMAP.keys():
            labels[lang] = row['prefLabel-%s' % lang].strip()
            includingNotes[lang] = row['includingNote-%s' % lang].strip()
            scopeNotes[lang] = row['scopeNote-%s' % lang].strip()
        add_class(row['fdcNumber'].strip(), labels, includingNotes, scopeNotes, BT, seeAlsos)

with open(glossary_file, 'rb') as gf:
    reader = csv.DictReader(gf)
    for row in reader:
        values = {}
        altLabels = {}
        hiddenLabels = {}
        for lang in LANGMAP.values():
            values[lang] = row['indexTerm-%s' % lang].strip()
            altLabels[lang] = row['altLabel-%s' % lang].strip().split('|')
            hiddenLabels[lang] = row['hiddenLabel-%s' % lang].strip().split('|')
        add_concept(row['conceptId'].strip(), row['fdcNumber'].strip(), values, altLabels, hiddenLabels)

with open(metadata_file, 'rb') as mf:
    reader = csv.DictReader(mf)
    for row in reader:
        values = {}
        for lang in LANGMAP.keys():
            values[lang] = row['Value-%s' % lang].strip()
        add_metadata(row['Field'].strip(), values)


# enrich scope notes with hyperlinks
def concept_link(match):
    code = match.group(0)
    uri = class_uri(code)
    if (uri, RDF.type, SKOS.Concept) in g:
        # concept exists - make it a hyperlink
        return '<a href="%s">%s</a>' % (uri, code)
    else:
        # no such concept, use just a plain code
        return code

for conc,note in g.subject_objects(SKOS.scopeNote):
    newnote = re.sub('\d+(\.\d+)*(/\.\d+)?', concept_link, note)
    if newnote != unicode(note):
        g.remove((conc, SKOS.scopeNote, note))
        g.add((conc, SKOS.scopeNote, Literal(newnote, note.language)))

g.serialize(destination=sys.stdout, format='turtle')
