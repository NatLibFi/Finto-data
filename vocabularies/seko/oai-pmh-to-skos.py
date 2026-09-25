#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from zoneinfo import ZoneInfo
from lxml.etree import tostring
import pymarc
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
import sys
import urllib
import io
import logging
import json 
import re

# slightly altered version of oai-pmh-to-skos.py from tools directory 

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
RDAU=Namespace("http://rdaregistry.info/Elements/u/")
SEKO=Namespace("http://urn.fi/urn:nbn:fi:au:seko:")

# simple regex to perform basic validation of URIs/IRIs
IRI = re.compile(r'^[^\x00-\x20<>"{}|^`\\]*$')


class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""

    def __call__(self, element):
        handler = marcxml.XmlHandler(strict=True, normalize_form='NFC')
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]


g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('dc', DC)
g.namespace_manager.bind('dct', DCT)
g.namespace_manager.bind('rdau', RDAU)
g.namespace_manager.bind('seko', SEKO)

if len(sys.argv) not in (2,3,4,5):
    print("Usage: %s <concept-namespace-URI> [<vocab-id>,<vocab-id>] [<default-link-vocab>] [<lang-override>]" % sys.argv[0], file=sys.stderr)
    sys.exit(1)

concns = sys.argv[1]
if len(sys.argv) >= 3:
    vocabids = sys.argv[2].split(',')
else:
    vocabids = None

if len(sys.argv) >= 4:
    linkvocabid = sys.argv[3]
else:
    linkvocabid = None

if len(sys.argv) == 5:
    langoverride = sys.argv[4]
else:
    langoverride = None

urins = concns[:-1]
metans = urins[:-1] + "-meta/"

g.namespace_manager.bind(metans.split('/')[-2], Namespace(metans))

LANGMAP = {
    'fin': 'fi',
    'swe': 'sv',
}

LINKLANGMAP = {
    'cilla': 'sv',
    'musa': 'fi',
    'ysa': 'fi',
}

RELCODE = {
    'na': SKOS.exactMatch,
    'nb': SKOS.closeMatch,
}

# temporary dicts to store label/URI mappings between passes
labelmap = {}    # key: prefLabel, val: URIRef
altlabelmap = {} # key: altLabel, val: URIRef
relationmap = {} # key: prefLabel, val: [ (property, prefLabel), ... ]
uri_to_label = {} # key: URIRef, val: prefLabel

RELMAP = { # MARC21 control field w value to RDF property + inverse
    'g': (SKOS.broader, SKOS.narrower),
    'h': (SKOS.narrower, SKOS.broader),
    'a': (RDAU.P60683, RDAU.P60686), # predecessor, successor
    'b': (RDAU.P60686, RDAU.P60683), # successor, predecessor
    None: (SKOS.related, SKOS.related),
}


def combined_label(f):
    labels = f.get_subfields('a', 'x', 'z')
    label = ' -- '.join(labels)
    hiddenlabel = ' '.join(labels)
    if hiddenlabel == label:
        hiddenlabel = None
    return (label, hiddenlabel)


def format_timestamp(ts):
    year = int(ts[0:2])
    if year >= 68:  # see https://www.loc.gov/marc/yr2000.html
        year += 1900
    else:
        year += 2000
    mon = int(ts[2:4])
    day = int(ts[4:6])
    if len(ts) > 6:
        h = int(ts[6:8])
        m = int(ts[8:10])
        s = int(ts[10:12])
        dt = datetime.now(ZoneInfo("Europe/Helsinki"))
        tzh = dt.strftime('%z')[:3]
        tzm = dt.strftime('%z')[3:]
        return f"{year:04d}-{mon:02d}-{day:02d}T{h:02d}:{m:02d}:{s:02d}{tzh:03s}:{tzm:02s}"
    else:
        return "%04d-%02d-%02d" % (year, mon, day)

# see if a concept exists in lcmpt 
# returns the uri or false if the there is no such label
def lookup(label):
  params = urllib.urlencode({'label': label.encode('utf-8'), 'format': 'application/json', 'lang': 'en'})
  api = 'http://skosmos.dev.finto.fi/rest/v1/lcmpt/lookup?' 
  url = api + params 
  try:
    response = json.load(urllib2.urlopen(url))
    return response['result'][0]['uri']
  except:
    return False

# Pass 1: convert to basic SKOS, without concept relations
for lineidx, line in enumerate(sys.stdin):
    file = io.StringIO(line)
    try:
        rec = pymarc.marcxml.parse_xml_to_array(file)[0]
    except Exception as e:
        logging.warning("Parse error on line %d, skipping record: %s", lineidx+1, e)

    if vocabids is not None:
        if rec['040']['f'].lower() not in vocabids:
            # wrong vocab id - skip this record
            continue

    if '889' in rec: # Melinda
        uri = URIRef(concns + rec['889']['c'])
    elif '024' in rec: # Seko / Fennica (proposed concepts with allocated URI)
        if 'seko' in vocabids and 76316 <= int(rec['001'].value()) <= 77539:
            continue
        uri = URIRef(rec['024']['a'])
    else: # Fennica / Alma / Viola
        uri = URIRef(concns + rec['001'].value())

    g.add((uri, SKOS.inScheme, URIRef(urins)))
    g.add((uri, RDF.type, SKOS.Concept))

    if langoverride is not None:
        lang = langoverride
    else:
        try:
            lang = LANGMAP[rec['040']['b']]
        except KeyError:
            print("Unknown 040b value for concept <%s>, skipping record" % uri, file=sys.stderr)
            continue

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
    
    # prefLabel (150/151/162)
    if '150' in rec:
        prefLabel, hiddenLabel = combined_label(rec['150'])
    elif '162' in rec:
        prefLabel, hiddenLabel = combined_label(rec['162']) 
    else:
        prefLabel, hiddenLabel = combined_label(rec['151'])
        g.add((uri, RDF.type, URIRef(metans + "GeographicalConcept")))
    g.add((uri, SKOS.prefLabel, Literal(prefLabel, lang)))
    if hiddenLabel is not None:
        g.add((uri, SKOS.hiddenLabel, Literal(hiddenLabel, lang)))
    labelmap[prefLabel] = uri
    uri_to_label[uri] = prefLabel
    
    # altLabel (450/451/462)
    for f in rec.get_fields('450') + rec.get_fields('451') + rec.get_fields('462'):
        altLabel, hiddenLabel = combined_label(f)
        g.add((uri, SKOS.altLabel, Literal(altLabel, lang)))
        if hiddenLabel is not None:
            g.add((uri, SKOS.hiddenLabel, Literal(hiddenLabel, lang)))
        altlabelmap[altLabel] = uri
    
    relationmap.setdefault(uri, [])
    
    # concept relations (550/551/562)
    for f in rec.get_fields('550') + rec.get_fields('551') + rec.get_fields('562'):

        relation = f['w'] if 'w' in f and f['w'] else None
        props = RELMAP[relation]
        if props is None:
            print("%s '%s': Unknown w subfield value '%s', ignoring field" % (uri, prefLabel, f['w']), file=sys.stderr)
        else:
            relationmap[uri].append((props, combined_label(f)[0]))
        
    # source (670)
    for f in rec.get_fields('670'):
        if 'u' in f: # URI link
            text = '; '.join(f.get_subfields('a','b'))
            if IRI.match(f['u']):
                g.add((uri, SKOS.closeMatch, URIRef(f['u'])))
            else:
                print("%s '%s': Bad link target URI '%s'" % (uri, prefLabel, f['u']), file=sys.stderr)
        else:
            text = f.format_field()
        while text.startswith(u'Lähde:'):
            text = text.replace(u'Lähde:', '').strip()
        while text.startswith(u'Källa:'):
            text = text.replace(u'Källa:', '').strip()
        g.add((uri, DC.source, Literal(text, lang)))
    
    # definition (677)
    for f in rec.get_fields('677'):
        text = f.format_field()
        g.add((uri, SKOS.definition, Literal(text, lang)))

    # note (680)
    for f in rec.get_fields('680'):
        text = f.format_field()
        g.add((uri, SKOS.note, Literal(text, lang)))
    
    # links to other authorities (750/751/762)
    for f in rec.get_fields('750') + rec.get_fields('751') + rec.get_fields('762'):
        if f.indicator2 == '7':
            vid = f['2'] # target vocabulary id
        else:
            vid = 'vocab' + f.indicators[1] # 0: LCSH, 1: LC Children's Subjects, 2: MesH etc.
        if vid is not None:
            vid = vid.lower()
        mappingrel = RELCODE.get(f['w'], SKOS.closeMatch)
        linklang = LINKLANGMAP.get(vid, None)
        if linklang is None: # not a vocabulary code used for internal linking between local MARC authority files
            if '0' in f and f['0'] is not None:
                if IRI.match(f['0']):
                    g.add((uri, mappingrel, URIRef(f['0'])))
                else:
                    print("%s '%s': Bad link target URI '%s'" % (uri, prefLabel, f['0']), file=sys.stderr)
                continue
            elif vid == 'lcmpt':
                #target_uri = lookup(combined_label(f)[0])
                target_uri = None
                if target_uri:
                    g.add((uri, mappingrel, URIRef(target_uri)))
                else:
                    print("%s '%s': Unknown target vocabulary '%s' for linked term '%s'" % (uri, prefLabel, f['2'], combined_label(f)[0]), file=sys.stderr)
                continue
            elif linkvocabid is not None and linkvocabid in LINKLANGMAP:
                linklang = LINKLANGMAP[linkvocabid]
                print("%s '%s': Unknown target vocabulary '%s' for linked term '%s', assuming '%s'" % (uri, prefLabel, f['2'], combined_label(f)[0], linkvocabid).encode('UTF-8'), file=sys.stderr)
            else:
                print("%s '%s': Unknown target vocabulary '%s' for linked term '%s'" % (uri, prefLabel, f['2'], combined_label(f)[0]), file=sys.stderr)
                continue
        g.add((uri, SKOS.prefLabel, Literal(combined_label(f)[0], linklang)))
    
# Pass 2: add concept relations now that URIs are known for all concepts
for uri in relationmap:
    for props, label in relationmap[uri]:
        if label in labelmap:
            target = labelmap[label]
        elif label in altlabelmap:
            target = altlabelmap[label]
            print("%s '%s': Referred term '%s' is an altLabel; should be '%s'" % (uri, uri_to_label[uri], label, uri_to_label[target]), file=sys.stderr)
        else:
            print("%s '%s': Unknown referred term '%s'" % (uri, uri_to_label[uri], label), file=sys.stderr)
            continue
        prop, invprop = props
        g.add((uri, prop, target))
        g.add((target, invprop, uri))

g.serialize(destination=sys.stdout.buffer, format='turtle')
