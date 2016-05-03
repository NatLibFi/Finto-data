#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import SKOS, XSD, OWL
from rdflib.namespace import DCTERMS as DCT

from pymarc import Record, Field, XMLWriter

import sys
import datetime

RDAU=Namespace('http://rdaregistry.info/Elements/u/')
ISOTHES=Namespace('http://purl.org/iso25964/skos-thes#')

VOCABCODE = 'yso'
PRIMARYLANG = 'fi'
LANGUAGES = {
    'fi': 'fin',
    'sv': 'swe',
    'en': 'eng',
}
SEEALSOPROPS = {
    SKOS.broader : 'g',
    SKOS.narrower : 'h',
    SKOS.related : None,
    RDAU.P60683 : 'a',
    RDAU.P60686 : 'b'
}

LEADER = '00000nz  a2200000n  4500'
CODES = ' n a z  bab              ana      '


g = Graph()
g.parse(sys.argv[1], format='turtle')
writer = XMLWriter(sys.stdout)



def format_language(langcode):
    return '<LNG>' + LANGUAGES.get(langcode, PRIMARYLANG)
    
def preflabel_of(conc):
    labels = g.preferredLabel(conc, lang=PRIMARYLANG)
    try:
        return labels[0][1]
    except IndexError:
        print >>sys.stderr, "WARNING: couldn't find label of %s, result: %s" % (conc,labels)
        return ''

for conc in sorted(g.subjects(RDF.type, SKOS.Concept)):
    if (conc, OWL.deprecated, Literal(True)) in g:
        continue
    rec = Record(leader=LEADER)
    
    # URI -> 001
    rec.add_field(
        Field(
            tag='001',
            data=conc
        )
    )
    
    # dct:modified -> 005
    mod = g.value(conc, DCT.modified, None)
    if mod is None:
        modified = datetime.date(2000, 1, 1)
    else:
        modified = mod.toPython() # datetime.date or datetime.datetime object
    rec.add_field(
        Field(
            tag='005',
            data=modified.strftime('%Y%m%d%H%M%S.0')
        )
    )
    
    # dct:created -> 008
    crt = g.value(conc, DCT.modified, None)
    if crt is None:
        created = datetime.date(2000, 1, 1)
    else:
        created = crt.toPython() # datetime.date or datetime.datetime object
    rec.add_field(
        Field(
            tag='008',
            data=created.strftime('%Y%m%d') + CODES
        )
    )
    
    # 040
    rec.add_field(
        Field(
            tag='040',
            indicators = [' ', ' '],
            subfields = [ 'a', 'FiNL',
                          'b', LANGUAGES[PRIMARYLANG],
                          'f', VOCABCODE ]
        )
    )
    
    # ConceptGroup / skos:member -> 072
    for group in sorted(g.subjects(SKOS.member, conc)):
        if (group, RDF.type, ISOTHES.ConceptGroup) not in g:
            continue
        # group code: first try using skos:notation, otherwise extract from label
        groupno = g.value(group, SKOS.notation, None)
        if groupno is None:
            label = preflabel_of(group)
            groupno = label.split(' ', 1)[0]
        rec.add_field(
            Field(
                tag='072',
                indicators = '  ',
                subfields=['a', VOCABCODE + groupno]
            )
        )
            

    # skos:prefLabel -> 150
    for prefLabel in sorted(g.objects(conc, SKOS.prefLabel), key=lambda v:v.language):
        rec.add_field(
            Field(
                tag='150',
                indicators = [' ', ' '],
                subfields=[ 'a', unicode(prefLabel),
                            '9', format_language(prefLabel.language) ]
            )
        )
    
    # skos:altLabel -> 450
    for altLabel in sorted(g.objects(conc, SKOS.altLabel), key=lambda v:v.language):
        rec.add_field(
            Field(
                tag='450',
                indicators = [' ', ' '],
                subfields=[ 'a', unicode(altLabel),
                            '9', format_language(altLabel.language) ]
            )
        )
    
    # broader/narrower/related/successor/predecessor -> 550
    
    for prop, wval in SEEALSOPROPS.items():
        for target in sorted(g.objects(conc, prop)):
            if (target, OWL.deprecated, Literal(True)) in g:
                continue # skip deprecated concepts
            label = preflabel_of(target)
            if wval is not None:
                subfields = [ 'w', wval,
                              'a', unicode(label) ]
            else:
                subfields = [ 'a', unicode(label) ]
            
            rec.add_field(
                Field(
                    tag='550',
                    indicators = [' ', ' '],
                    subfields = subfields
                )
            )    
    
    # skos:note -> 680
    for note in sorted(g.objects(conc, SKOS.note), key=lambda v:v.language):
        rec.add_field(
            Field(
                tag='680',
                indicators = [' ', ' '],
                subfields=[ 'i', unicode(note),
                            '9', format_language(note.language) ]
            )
        )
    
    # TODO 750 links to ysa/allars/lcsh - need to look up labels for the URIs

    writer.write(rec)


writer.close()
