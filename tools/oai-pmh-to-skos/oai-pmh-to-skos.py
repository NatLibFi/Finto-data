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
import pytz

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")

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


if len(sys.argv) not in (4,5,6,7):
    print >>sys.stderr, "Usage: %s <oai-pmh-provider> <set-name> <concept-namespace-URI> [<vocab-id>] [<default-link-vocab>] [<lang-override>]" % sys.argv[0]
    sys.exit(1)

provider, setname, concns = sys.argv[1:4]
if len(sys.argv) >= 5:
    vocabid = sys.argv[4]
else:
    vocabid = None

if len(sys.argv) >= 6:
    linkvocabid = sys.argv[5]
else:
    linkvocabid = None

if len(sys.argv) == 7:
    langoverride = sys.argv[6]
else:
    langoverride = None

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
    'cilla': 'sv',
    'musa': 'fi',
    'ysa': 'fi',
}

# temporary dicts to store label/URI mappings between passes
labelmap = {}    # key: prefLabel, val: URIRef
altlabelmap = {} # key: altLabel, val: URIRef
relationmap = {} # key: prefLabel, val: [ (property, prefLabel), ... ]
uri_to_label = {} # key: URIRef, val: prefLabel

RELMAP = { # MARC21 control field w value to RDF property + inverse
    'g': (SKOS.broader, SKOS.narrower),
    'h': (SKOS.narrower, SKOS.broader),
    'a': (DCT.replaces, DCT.isReplacedBy),
    'b': (DCT.isReplacedBy, DCT.replaces),
    None: (SKOS.related, SKOS.related),
}

def combined_label(f):
    labels = f.get_subfields('a', 'x', 'z')
    label = ' -- '.join(labels)
    hiddenlabel = ' '.join(labels)
    if hiddenlabel == label:
        hiddenlabel = None
    return (label, hiddenlabel)


helsinki=pytz.timezone('Europe/Helsinki')

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
        dt = datetime(year, mon, day, h, m, s)
        tzdt = helsinki.localize(dt)
        return tzdt.isoformat()
        
        # return "%04d-%02d-%02dT%02d:%02d:%02d" % (year, mon, day, h, m, s)
    else:
        return "%04d-%02d-%02d" % (year, mon, day)

# Pass 1: convert to basic SKOS, without concept relations
for count, oaipmhrec in enumerate(recs):
#    if count % 10 == 0: print >>sys.stderr, "count: %d" % count
    rec = oaipmhrec[1] # MARCXML record

    if vocabid is not None:
        if vocabid != rec['040']['f'].lower():
            # wrong vocab id - skip this record
            continue

    if '889' in rec: # Melinda
        uri = URIRef(concns + rec['889']['c'])
    else: # Fennica / Alma / Viola
        uri = URIRef(concns + rec['001'].value())
    g.add((uri, SKOS.inScheme, URIRef(urins)))
    g.add((uri, RDF.type, SKOS.Concept))
    
    if langoverride is not None:
        lang = langoverride
    else:
        lang = LANGMAP[rec['040']['b']]

    # created timestamp
    created = rec['008'].value()[:6]
    g.add((uri, DCT.created, Literal(format_timestamp(created), datatype=XSD.date)))

    # modified timestamp
    modified = rec['005'].value()[2:14] # FIXME ugly...discards century info
    g.add((uri, DCT.modified, Literal(format_timestamp(modified), datatype=XSD.dateTime)))
    
    # thematic group (072)
    for f in rec.get_fields('072'):
        groupid = f['a'][3:].strip()
        if groupid != '':
            groupuri = URIRef(urins + "ryhma_" + groupid)
            g.add((groupuri, SKOS.member, uri))
    
    # prefLabel (150/151)
    if '150' in rec:
        prefLabel, hiddenLabel = combined_label(rec['150'])
    else:
        prefLabel, hiddenLabel = combined_label(rec['151'])
        g.add((uri, RDF.type, URIRef(metans + "GeographicalConcept")))
    g.add((uri, SKOS.prefLabel, Literal(prefLabel, lang)))
    if hiddenLabel is not None:
        g.add((uri, SKOS.hiddenLabel, Literal(hiddenLabel, lang)))
    labelmap[prefLabel] = uri
    uri_to_label[uri] = prefLabel
    
    # altLabel (450/451)
    for f in rec.get_fields('450') + rec.get_fields('451'):
        altLabel, hiddenLabel = combined_label(f)
        g.add((uri, SKOS.altLabel, Literal(altLabel, lang)))
        if hiddenLabel is not None:
            g.add((uri, SKOS.hiddenLabel, Literal(hiddenLabel, lang)))
        altlabelmap[altLabel] = uri
    
    relationmap.setdefault(uri, [])
    
    # concept relations (550/551)
    for f in rec.get_fields('550') + rec.get_fields('551'):
        props = RELMAP.get(f['w'], None)
        if props is None:
            print >>sys.stderr, ("%s '%s': Unknown w subfield value '%s', ignoring field" % (uri, prefLabel, f['w'])).encode('UTF-8')
        else:
            relationmap[uri].append((props, combined_label(f)[0]))
        
    # source (670)
    for f in rec.get_fields('670'):
        text = f.format_field()
        while text.startswith(u'Lähde:'):
            text = text.replace(u'Lähde:', '').strip()
        while text.startswith(u'Källa:'):
            text = text.replace(u'Källa:', '').strip()
        g.add((uri, DC.source, Literal(text, lang)))
    
    # scope note (680)
    for f in rec.get_fields('680'):
        text = f.format_field()
        g.add((uri, SKOS.scopeNote, Literal(text, lang)))
    
    # links to other authorities (750/751)
    for f in rec.get_fields('750') + rec.get_fields('751'):
        vid = f['2'] # target vocabulary id
        if vid is not None: vid = vid.lower()
        linklang = LINKLANGMAP.get(vid, None)
        if linklang is None:
            if linkvocabid is not None and linkvocabid in LINKLANGMAP:
                linklang = LINKLANGMAP[linkvocabid]
                print >>sys.stderr, ("%s '%s': Unknown target vocabulary '%s' for linked term '%s', assuming '%s'" % (uri, prefLabel, f['2'], combined_label(f)[0], linkvocabid)).encode('UTF-8')
            else:
                print >>sys.stderr, ("%s '%s': Unknown target vocabulary '%s' for linked term '%s'" % (uri, prefLabel, f['2'], combined_label(f)[0])).encode('UTF-8')
                continue
        g.add((uri, SKOS.prefLabel, Literal(combined_label(f)[0], linklang)))
    
# Pass 2: add concept relations now that URIs are known for all concepts
for uri, rels in relationmap.iteritems():
    for props, label in rels:
        if label in labelmap:
            target = labelmap[label]
        elif label in altlabelmap:
            target = altlabelmap[label]
            print >>sys.stderr, ("%s '%s': Referred term '%s' is an altLabel; should be '%s'" % (uri, uri_to_label[uri], label, uri_to_label[target])).encode('UTF-8')
        else:
            print >>sys.stderr, ("%s '%s': Unknown referred term '%s'" % (uri, uri_to_label[uri], label)).encode('UTF-8')
            continue
        prop, invprop = props
        g.add((uri, prop, target))
        g.add((target, invprop, uri))

g.serialize(format='turtle', destination=sys.stdout)
