#!/usr/bin/env python

# adapted from https://gist.github.com/lawlesst/1323535

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
import os.path

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
OWL=Namespace("http://www.w3.org/2002/07/owl#")
CN=Namespace("http://urn.fi/URN:NBN:fi:au:cn:")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")
RDAA=Namespace("http://rdaregistry.info/Elements/a/")
RDAC=Namespace("http://rdaregistry.info/Elements/c/")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
ISNI=Namespace("http://isni.org/isni/")

LAS_IDENTIFY_URL="http://demo.seco.tkk.fi/las/identify"
FINTO_API_BASE="http://api.finto.fi/rest/v1/"

LANG_CACHE_FILE='lang_cache.txt'


# mnemonics for RDA URIs
CorporateBody=RDAC.C10005
preferredNameForTheCorporateBody=RDAA.P50041
variantNameForTheCorporateBody=RDAA.P50025
otherDesignationAssociatedWithTheCorporateBody=RDAA.P50033
typeOfCorporateBody=RDAA.P50237
typeOfJurisdiction=RDAA.P50238
relatedCorporateBody=RDAA.P50218
predecessor=RDAA.P50012
successor=RDAA.P50016
hierarchicalSuperior=RDAA.P50008
hierarchicalSubordinate=RDAA.P50010
corporateHistory=RDAA.P50035
placeAssociatedWithTheCorporateBody=RDAA.P50031
fieldOfActivityOfTheCorporateBody=RDAA.P50022
languageOfTheCorporateBody=RDAA.P50023
dateOfEstablishment=RDAA.P50037
dateOfTermination=RDAA.P50038

class MARCXMLReader(object):
  """Returns the PyMARC record from the OAI structure for MARC XML"""
  
  def __call__(self, element):
    #print element[0][1].text
    handler = marcxml.XmlHandler(strict=True, normalize_form='NFC')
    marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
    return handler.records[0]


def lookup_mts(label):
  payload = {'label': label, 'lang': 'fi'}
  req = requests.get(FINTO_API_BASE + 'mts/lookup', params=payload)
  if req.status_code != 200:
    return None

  return URIRef(req.json()['result'][0]['uri'])

def guess_language(text):
  """return the most likely language for the given unicode text string"""
  if text not in lang_cache:
    retries = 0
    lang = None
    certainty = None
    while retries < 10:
      r = requests.get(LAS_IDENTIFY_URL, params={'text': text})
      if r.status_code == 200 and len(r.text) > 0:
        lang = r.json()['locale']
        certainty = r.json()['certainty']
        break
      retries += 1
      print >>sys.stderr, "Request to LAS failed (status code %d, response length %d)" % (r.status_code, len(r.text))
      print >>sys.stderr, "- retrying %d, url: '%s'" % (retries, r.url)

    if certainty is None:
      print >>sys.stderr, "Giving up LAS identify request for text '%s' for uri <%s>" % (text.encode('UTF-8'), uri)

    if lang in ('fi','sv','en') or certainty >= 0.5:
      lang_cache[text] = lang
    else:
      lang_cache[text] = None # too hard to know
  return lang_cache[text]

def format_label(fld, skip_last=False):
  """return a label consisting of subfields in a Field, properly formatted"""
  subfields = fld.get_subfields('a','b','n','d','c')
  
  if len(subfields) > 0:
    if skip_last:
      subfields = subfields[:-1]
    return ' '.join(subfields)
  else:
    return None

def format_timestamp(ts):
  year = int(ts[0:2])
  if year >= 90:
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

def convert_record(oaipmhrec):
  id = oaipmhrec[0].identifier().split(':')[-1]
  rec = oaipmhrec[1] # MARCXML record
  if '110' not in rec and '111' not in rec: return # empty record (deleted?)
  
  uri = CN[id]
  g.add((uri, RDF.type, SKOS.Concept))
  g.add((uri, RDF.type, CorporateBody))
  if '110' in rec:
    label = format_label(rec['110'])
  else:
    label = format_label(rec['111'])
  label_to_uri[label] = uri
  literal = Literal(label, lang='fi') # prefLabel is always Finnish
  g.add((uri, SKOS.prefLabel, literal))
  g.add((uri, preferredNameForTheCorporateBody, literal))
  if '110' in rec and rec['110']['a'] != label:
    superior = format_label(rec['110'], skip_last=True)
    if superior.endswith('.'): superior = superior[:-1] # strip final period
    g.add((uri, hierarchicalSuperior, Literal(superior)))

  # created timestamp
  created = rec['008'].value()[:6]
  g.add((uri, DCT.created, Literal(format_timestamp(created), datatype=XSD.date)))

  # modified timestamp
  modified = rec['005'].value()[2:14] # FIXME ugly...discards century info
  g.add((uri, DCT.modified, Literal(format_timestamp(modified), datatype=XSD.dateTime)))
  
  # ISNI
  for f in rec.get_fields('024'):
    if '2' in f and f['2'] == 'isni' and 'a' in f:
      isni = ISNI[f['a']]
      g.add((uri, SKOS.closeMatch, isni))

  if '046' in rec:
    fld = rec['046']
    if 's' in fld:
      g.add((uri, dateOfEstablishment, Literal(fld['s'])))
    if 't' in fld:
      g.add((uri, dateOfTermination, Literal(fld['t'])))
  
  for f in rec.get_fields('368'):
    #print uri, "368", f.as_marc('utf8')
    if 'a' in f:
      prop = typeOfCorporateBody
      val = f['a']
    elif 'b' in f:
      prop = typeOfJurisdiction
      val = f['b']
    elif 'c' in f:
      prop = otherDesignationAssociatedWithTheCorporateBody
      val = f['c']
    else:
      print >>sys.stderr, "Could not parse 368 value for <%s>, skipping" % uri
      continue

    obj = Literal(val, lang='fi') # by default, use a literal value
    if '2' in f and f['2'] == 'mts':
      # try to see if we can use a URI value from MTS instead
      mtsuri = lookup_mts(val)
      if mtsuri is not None:
        obj = mtsuri

    g.add((uri, prop, obj))

  for f in rec.get_fields('370'):
    if 'e' in f:
      # TODO: temporal dimensions in $s/$t
      g.add((uri, placeAssociatedWithTheCorporateBody, Literal(f['e'], lang='fi')))

  for f in rec.get_fields('372'):
    if 'a' in f:
      g.add((uri, fieldOfActivityOfTheCorporateBody, Literal(f['a'], lang='fi')))

  for f in rec.get_fields('377'):
    if 'a' in f:
      g.add((uri, languageOfTheCorporateBody, Literal(f['a'])))

  for f in rec.get_fields('410') + rec.get_fields('411'):
    varname = format_label(f)
    if varname is None:
      print >>sys.stderr, "Empty 410/411 value for <%s>, skipping" % uri
      return
    if len(varname) < 5 or ('w' in f and f['w'] == 'd'): # is very short, or an acronym
      varlit = Literal(varname) # no language tag for acronyms (too hard!)
    else:
      varlit = Literal(varname, lang=guess_language(varname))
    g.add((uri, SKOS.altLabel, varlit))
    g.add((uri, variantNameForTheCorporateBody, varlit))

  for f in rec.get_fields('510') + rec.get_fields('511'):
    rdarel = relatedCorporateBody # default relationship
    if 'w' in f:
      if f['w'] == 'a':
        rdarel = predecessor
      elif f['w'] == 'b':
        rdarel = successor
      elif f['w'] == 't':
        rdarel = hierarchicalSuperior
      else:
        print >>sys.stderr, "unknown 510/511 $w value for <%s>:" % uri, f['w']

    targetname = format_label(f)
    if targetname is not None:
      # target is now a Literal, it will be converted to resource in Pass 2
      g.add((uri, rdarel, Literal(targetname)))

  for f in rec.get_fields('670'):
    g.add((uri, DC.source, Literal(f.format_field(), lang='fi')))

  for f in rec.get_fields('678'):
    g.add((uri, corporateHistory, Literal(f.format_field(), lang='fi')))

# initialize OAI-PMH and MARC handling

marcxml_reader = MARCXMLReader()
registry = metadata.MetadataRegistry()
registry.registerReader('marc21', marcxml_reader)

# initialize output RDF graph

g = Graph()
g.namespace_manager.bind('skos', SKOS)
g.namespace_manager.bind('cn', CN)
g.namespace_manager.bind('dc', DC)
g.namespace_manager.bind('dct', DCT)
g.namespace_manager.bind('rdaa', RDAA)
g.namespace_manager.bind('rdac', RDAC)

# initialize language determination cache

lang_cache = {}
if os.path.exists(LANG_CACHE_FILE):
  lcf = codecs.open(LANG_CACHE_FILE, 'r', 'utf-8')
  for line in lcf:
    lang, text = line.rstrip("\r\n").split("\t")
    if lang == '': lang = None
    lang_cache[text] = lang
  lcf.close()  

label_to_uri = {}

# pass 1: convert MARC data to basic RDF

oai = Client('https://fennica.linneanet.fi/cgi-bin/oai-pmh-fennica-asteri-aut.cgi', registry)

#recs = oai.listRecords(metadataPrefix='marc21', set='corporateNames', from_=datetime(2019,05,15))
recs = oai.listRecords(metadataPrefix='marc21', set='corporateNames')
for oaipmhrec in recs:
  convert_record(oaipmhrec)

recs = oai.listRecords(metadataPrefix='marc21', set='meetingNames')
for oaipmhrec in recs:
  convert_record(oaipmhrec)

# pass 2: convert literal values to resources

for prop in (relatedCorporateBody, predecessor, successor, hierarchicalSuperior):
  for s,o in g.subject_objects(prop):
    if isinstance(o, Literal):
      g.remove((s,prop,o)) # remove original
      res = label_to_uri.get(u"%s" % o, None)
      if res is None:
        print >>sys.stderr, ("no resource found for '%s' (subject <%s>)" % (o, s)).encode('UTF-8')
      else:
        g.add((s,prop,res))
        if prop == hierarchicalSuperior:
          g.add((res,hierarchicalSubordinate,s)) # add inverse relationship
          g.add((s,SKOS.broader,res)) # also add skos:broader relationship to make a tree

# store language determination cache

lcf = codecs.open(LANG_CACHE_FILE, 'w', 'utf-8')
for text in sorted(lang_cache.keys()):
  lang = lang_cache[text]
  if lang is None: lang = ''
  print >>lcf, "%s\t%s" % (lang, text)
lcf.close()

# serialize output RDF

g.serialize(destination=sys.stdout, format='turtle')
