#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oaipmh.client import Client
from oaipmh import metadata
from lxml.etree import tostring
from pymarc import marcxml
from cStringIO import StringIO
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
from datetime import datetime
import requests
import sys
import codecs

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
  
    def __call__(self, element):
        handler = marcxml.XmlHandler(strict=True, normalize_form='NFC')
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

marcxml_reader = MARCXMLReader()
registry = metadata.MetadataRegistry()
registry.registerReader('marc21', marcxml_reader)

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('dc', DC)
g.namespace_manager.bind('dct', DCT)


if len(sys.argv) != 4:
    print >>sys.stderr, "Usage: %s <oai-pmh-provider> <set-name> <concept-namespace-URI>" % sys.argv[0]
    sys.exit(1)

provider, setname, concns = sys.argv[1:]
urins = concns[:-1]
metans = urins[:-1] + "-meta/"

g.namespace_manager.bind(metans.split('/')[-2], Namespace(metans))

oai = Client(provider, registry)
#recs = oai.listRecords(metadataPrefix='marc21', set=setname, from_=datetime(2014,10,1))
recs = oai.listRecords(metadataPrefix='marc21', set=setname)

LANGMAP = {
    'fin': 'fi',
    'swe': 'sv',
}

LINKLANGMAP = {
    'Cilla': 'sv',
    'ysa': 'fi',
}

# temporary dicts to store label/URI mappings between passes
labelmap = {}    # key: prefLabel, val: URIRef
relationmap = {} # key: prefLabel, val: [ (property, prefLabel), ... ]

RELMAP = { # MARC21 control field w value to RDF property + inverse
    'g': (SKOS.broader, SKOS.narrower),
    'h': (SKOS.narrower, SKOS.broader),
#    'a': (DCT.replaces, DCT.isReplacedBy),
#    'b': (DCT.isReplacedBy, DCT.replaces),
    'a': (SKOS.related, SKOS.related),
    'b': (SKOS.related, SKOS.related),
    None: (SKOS.related, SKOS.related),
}

def combined_label(f):
    labels = f.get_subfields('a', 'x', 'z')
    return ' -- '.join(labels)

def format_timestamp(ts):
    year = int(ts[0:2])
    if year >= 80:
        year += 1900
    else:
        year += 2000
    mon = int(ts[2:4])
    day = int(ts[4:6])
    if len(ts) > 6:
        h = int(ts[6:8])
        m = int(ts[8:10])
        s = int(ts[10:12])
        # TODO which time zone?
        return "%04d-%02d-%02dT%02d:%02d:%02d" % (year, mon, day, h, m, s)
    else:
        return "%04d-%02d-%02d" % (year, mon, day)

# Pass 1: convert to basic SKOS, without concept relations
for count, oaipmhrec in enumerate(recs):
#    if count % 10 == 0: print >>sys.stderr, "count: %d" % count
    rec = oaipmhrec[1] # MARCXML record
    if '889' in rec: # Melinda
        uri = URIRef(concns + rec['889']['c'])
    else: # Fennica / Alma / Viola
        uri = URIRef(concns + rec['001'].value())
    g.add((uri, SKOS.inScheme, URIRef(urins)))
    g.add((uri, RDF.type, SKOS.Concept))
    
    lang = LANGMAP[rec['040']['b']]

    # created timestamp
    created = rec['008'].value()[:6]
    #g.add((uri, DCT.created, Literal(format_timestamp(created))))

    # modified timestamp
    modified = rec['005'].value()[2:14] # FIXME ugly...discards century info
    #g.add((uri, DCT.modified, Literal(format_timestamp(modified))))
    
    # thematic group (072)
    for f in rec.get_fields('072'):
        groupid = f['a'][3:].strip()
        if groupid != '':
            #groupuri = URIRef(urins + "ryhma_" + groupid)
            groupuri = URIRef("http://www.yso.fi/onto/ysa/" + "ryhma_" + groupid)
            g.add((groupuri, SKOS.member, uri))
    
    # prefLabel (150/151)
    if '150' in rec:
        prefLabel = combined_label(rec['150'])
    else:
        prefLabel = combined_label(rec['151'])
        g.add((uri, RDF.type, URIRef(metans + "GeographicalConcept")))
    g.add((uri, SKOS.prefLabel, Literal(prefLabel, lang)))
    labelmap[prefLabel] = uri
    
    # altLabel (450/451)
    for f in rec.get_fields('450') + rec.get_fields('451'):
        altLabel = combined_label(f)
        g.add((uri, SKOS.altLabel, Literal(altLabel, lang)))
    
    relationmap.setdefault(uri, [])
    
    # concept relations (550/551)
    for f in rec.get_fields('550') + rec.get_fields('551'):
        props = RELMAP.get(f['w'], None)
        if props is None:
            print >>sys.stderr, "%s: Unknown w subfield value '%s', ignoring field" % (uri, f['w'])
        else:
            relationmap[uri].append((props, combined_label(f)))
        
    # source (670)
    for f in rec.get_fields('670'):
        text = f.format_field()
        while text.startswith(u'Lähde:'):
            text = text.replace(u'Lähde:', '').strip()
        while text.startswith(u'Källa:'):
            text = text.replace(u'Källa:', '').strip()
        #g.add((uri, DC.source, Literal(text, lang)))
        g.add((uri, URIRef(metans + "source"), Literal(text, lang)))
    
    # scope note (680)
    for f in rec.get_fields('680'):
        text = f.format_field()
        #g.add((uri, SKOS.scopeNote, Literal(text, lang)))
        g.add((uri, SKOS.note, Literal(text.strip(), lang)))
    
    # links to other authorities (750)
    for f in rec.get_fields('750'):
        linklang = LINKLANGMAP.get(f['2'], None)
        if linklang is None:
            print >>sys.stderr, ("%s: Unknown target vocabulary '%s' for linked term '%s'" % (uri, f['2'], combined_label(f))).encode('UTF-8')
        else:
            g.add((uri, SKOS.prefLabel, Literal(combined_label(f), linklang)))
    
# Pass 2: add concept relations now that URIs are known for all concepts
for uri, rels in relationmap.iteritems():
    for props, prefLabel in rels:
        try:
            target = labelmap[prefLabel]
            prop, invprop = props
            g.add((uri, prop, target))
            #g.add((target, invprop, uri))
        except KeyError:
            print >>sys.stderr, ("%s: Unknown label '%s'" % (uri, prefLabel)).encode('UTF-8')

g.serialize(format='turtle', destination=sys.stdout)
