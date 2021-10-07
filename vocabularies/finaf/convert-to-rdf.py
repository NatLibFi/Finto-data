#!/usr/bin/env python3

import sys
import io
import re
import functools
import logging
import csv
import unicodedata

import requests
import pymarc.marcxml
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
OWL=Namespace("http://www.w3.org/2002/07/owl#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")
RDAA=Namespace("http://rdaregistry.info/Elements/a/")
RDAC=Namespace("http://rdaregistry.info/Elements/c/")
RDAP=Namespace("http://rdaregistry.info/Elements/p/")
RDAU=Namespace("http://rdaregistry.info/Elements/u/")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
ISNI=Namespace("http://isni.org/isni/")
VIAF=Namespace("http://viaf.org/viaf/")
FINAF=Namespace("http://urn.fi/URN:NBN:fi:au:finaf:")

# mnemonics for RDA URIs
Person=RDAC.C10004
CorporateBody=RDAC.C10005
authorizedAccessPointForPerson=RDAA.P50411
authorizedAccessPointForCorporateBody=RDAA.P50407
preferredNameOfPerson=RDAA.P50117
variantNameOfPerson=RDAA.P50103
preferredNameOfCorporateBody=RDAA.P50041
variantNameOfCorporateBody=RDAA.P50025
fullerFormOfName=RDAA.P50115
birthYear=RDAA.P50121
deathYear=RDAA.P50120
periodOfActivityOfPerson=RDAA.P50098
dateOfEstablishment=RDAA.P50037
dateOfTermination=RDAA.P50038
periodOfActivityOfCorporateBody=RDAA.P50236
professionOrOccupation=RDAA.P50104
typeOfCorporateBody=RDAA.P50237
categoryOfGovernment=RDAA.P50238
placeOfBirth=RDAA.P50119
placeOfDeath=RDAA.P50118
countryAssociatedWithPerson=RDAA.P50097
placeOfResidence=RDAA.P50109
placeAssociatedWithPerson=RDAA.P50346
placeAssociatedWithCorporateBody=RDAA.P50350
fieldOfActivityOfPerson=RDAA.P50100
fieldOfActivityOfCorporateBody=RDAA.P50022
otherDesignationAssociatedWithPerson=RDAA.P50108
otherDesignationAssociatedWithCorporateBody=RDAA.P50033
isPersonMemberOfCorporateBody=RDAA.P50095
titleOfPerson=RDAA.P50110
languageOfPerson=RDAA.P50102
languageOfCorporateBody=RDAA.P50023
relatedPersonOfPerson=RDAA.P50316
relatedPersonOfCorporateBody=RDAA.P50334
relatedCorporateBodyOfPerson=RDAA.P50318
relatedCorporateBodyOfCorporateBody=RDAA.P50336
predecessor=RDAA.P50012
successor=RDAA.P50016
hierarchicalSuperior=RDAA.P50008
biographicalInformation=RDAA.P50113
corporateHistory=RDAA.P50035
noteOnPerson=RDAA.P50395
noteOnCorporateBody=RDAA.P50393
sourceConsulted=RDAU.P61101
identifierForPerson=RDAA.P50094
identifierForCorporateBody=RDAA.P50006

# properties whose values should be converted to resources if possible
literal_to_resource = [
    isPersonMemberOfCorporateBody,
    relatedPersonOfPerson,
    relatedPersonOfCorporateBody,
    relatedCorporateBodyOfPerson,
    relatedCorporateBodyOfCorporateBody,
    predecessor,
    successor,
    hierarchicalSuperior
]

nameOfPlace=RDAP.P70001

EDTF=URIRef('http://id.loc.gov/datatypes/edtf')

FINTO_API_BASE="http://api.finto.fi/rest/v1/"
FINTO_SPARQL_ENDPOINT="http://api.finto.fi/sparql"

def normalize_relterm(term):
    return re.sub(r'[.,: ]*$', '', term.lower().strip())

def load_relations(filename):
    rels = {}
    with open(filename) as relf:
        reader = csv.reader(relf)
        for idx, row in enumerate(reader):
            if idx == 0:
                continue # skip header
            term = normalize_relterm(row[0])
            if not term:
                continue
            rdacurie = row[2].strip()
            if not rdacurie:
                continue
            rdauri = RDAA[rdacurie.replace('rdaa:', '')]
            literal_to_resource.append(rdauri)
            rels[term] = rdauri
    return rels

def initialize_graph():
    g = Graph()
    g.namespace_manager.bind('skos', SKOS)
    g.namespace_manager.bind('finaf', FINAF)
    g.namespace_manager.bind('dc', DC)
    g.namespace_manager.bind('dct', DCT)
    g.namespace_manager.bind('rdaa', RDAA)
    g.namespace_manager.bind('rdac', RDAC)
    g.namespace_manager.bind('rdap', RDAP)
    g.namespace_manager.bind('rdau', RDAU)
    return g

def normalize(label):
    """normalize string to unicode Normal Form C (composed)"""
    return unicodedata.normalize('NFC', label)

def format_label(fld, skip_last=False):
    """return a label consisting of subfields in a Field, properly formatted"""
    subfields = fld.get_subfields('a','b','n','c','d','q')

    if len(subfields) > 0:
        if skip_last:
            subfields = subfields[:-1]
        return normalize(' '.join(subfields))
    else:
        return None

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
        # TODO which time zone?
        return "%04d-%02d-%02dT%02d:%02d:%02d" % (year, mon, day, h, m, s)
    else:
        return "%04d-%02d-%02d" % (year, mon, day)

@functools.lru_cache(maxsize=1000)
def lookup_mts(label):
    logging.debug('looking up MTS label "%s"', label)
    payload = {'label': label, 'lang': 'fi'}
    req = requests.get(FINTO_API_BASE + 'mts/lookup', params=payload)
    if req.status_code != 200:
        logging.debug('MTS lookup for "%s" failed', label)
        return None

    return URIRef(req.json()['result'][0]['uri'])


@functools.lru_cache(maxsize=1000)
def lookup_yso(label):
    logging.debug('looking up YSO label "%s"', label)
    payload = {'label': label, 'lang': 'fi'}
    req = requests.get(FINTO_API_BASE + 'yso/lookup', params=payload)
    if req.status_code != 200:
        logging.debug('YSO lookup for "%s" failed', label)
        return None

    return URIRef(req.json()['result'][0]['uri'])


@functools.lru_cache(maxsize=10000)
def lookup_yso_place(label):
    label = normalize(label)
    logging.debug('looking up YSO place "%s"', label)
    if ', ' in label:
        place, country = label.rsplit(', ', 1)
        country_uri = lookup_yso_place(country)
        if isinstance(country_uri, Literal):
            logging.debug('YSO place lookup for country "%s" failed', country)
            return Literal(label, 'fi')
        payload = {'query': place, 'parent': str(country_uri), 'lang': 'fi'}
        req = requests.get(FINTO_API_BASE + 'yso-paikat/search', params=payload)
        if req.status_code != 200:
            logging.debug('YSO place lookup for place "%s" failed (error)', place)
            return Literal(label, 'fi')
        results = req.json()['results']
        if results:
            return URIRef(results[0]['uri'])
        logging.debug('YSO place lookup for place "%s" failed (no results)', place)
        return Literal(label, 'fi')

    payload = {'label': label, 'lang': 'fi'}
    req = requests.get(FINTO_API_BASE + 'yso-paikat/lookup', params=payload)
    if req.status_code != 200:
        logging.debug('YSO place lookup for place "%s" failed', label)
        return Literal(label, 'fi')

    return URIRef(req.json()['result'][0]['uri'])

@functools.lru_cache(maxsize=1000)
def lookup_language(langcode):
    logging.debug('looking up language code "%s"', langcode)
    sparql = SPARQLWrapper(FINTO_SPARQL_ENDPOINT)
    sparql.setQuery("""
        SELECT ?lang
        FROM <http://lexvo.org/id/iso639-3/>
        WHERE { ?lang <http://lexvo.org/ontology#iso6392BCode> "%s" }
    """ % langcode)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        return URIRef(result["lang"]["value"])
    logging.debug('Language code lookup for "%s" failed', langcode)
    return None

def main():
    logging.basicConfig(level=logging.DEBUG)

    g = initialize_graph()

    label_to_uri = {}
    rel500i = load_relations('500i-to-rda.csv')
    rel510i = load_relations('510i-to-rda.csv')

    # Pass 1: convert MARC data to basic RDF
    for lineidx, line in enumerate(sys.stdin):
        file = io.StringIO(line)
        try:
            rec = pymarc.marcxml.parse_xml_to_array(file)[0]
        except Exception as e:
            logging.warning("Parse error on line %d, skipping record: %s", lineidx+1, e)
        
        recid = rec['001'].value()
        logging.info("Starting conversion of record %s", recid)

        uri = FINAF[recid]  # default unless URN found in record
        # see if the record contains a URN/URI
        for f in rec.get_fields('024'):
            if '2' in f and 'a' in f and f['2'] == 'finaf':
                logging.info('using URN from 024 field')
                uri = URIRef(f['a'])

        # sanity check
        if '100' not in rec and '110' not in rec and '111' not in rec:
            logging.warning('no 100/110/111 field, skipping record %s', recid)
            continue

        # exclude test records
        if 'STA' in rec and 'a' in rec['STA'] and rec['STA']['a'] == 'TEST':
            logging.info('skipping TEST record %s', recid)
            continue
        
        if '100' in rec: # person name
            g.add((uri, RDF.type, Person))
            label = format_label(rec['100'])
            labelprop = authorizedAccessPointForPerson
            is_person = True
        else: # corporate or meeting names
            g.add((uri, RDF.type, CorporateBody))
            f = rec.get_fields('110', '111')[0]
            label = format_label(f)
            labelprop = authorizedAccessPointForCorporateBody
            is_person = False
        g.add((uri, RDF.type, SKOS.Concept))
        literal = Literal(label, lang='fi') # prefLabel is always Finnish
        g.add((uri, SKOS.prefLabel, literal))
        g.add((uri, labelprop, literal))
        label_to_uri[label] = uri
        logging.debug("Preferred label: '%s'", label)

        # created timestamp
        created = rec['008'].value()[:6]
        g.add((uri, DCT.created, Literal(format_timestamp(created), datatype=XSD.date)))

        # modified timestamp
        modified = rec['005'].value()[2:14] # FIXME ugly...discards century info
        g.add((uri, DCT.modified, Literal(format_timestamp(modified), datatype=XSD.dateTime)))

        if is_person:
            id_prop = identifierForPerson
        else:
            id_prop = identifierForCorporateBody

        asteri_str = 'Asteri ID: {}'.format(recid)
        g.add((uri, id_prop, Literal(asteri_str)))

        # ISNI, ORCID, VIAF etc. identifiers & deprecated URNs
        for f in rec.get_fields('024'):
            if 'q' in f and f['q'].lower().startswith('yritys- ja yhteisötunnus') and 'a' in f:
                yt = f['a'].replace(' ', '')
                yt_str = 'Y-tunnus: {}'.format(yt)
                g.add((uri, id_prop, Literal(yt_str)))

            if 'z' in f and '2' in f and f['2'] == 'urn':
                urn = f['z'].replace(' ', '')
                urn_uri = URIRef(urn)
                g.add((urn_uri, DCT.isReplacedBy, uri))

            if '2' not in f or 'a' not in f:
                continue

            if f['2'] == 'isni':
                isni = f['a'].replace(' ', '')
                isni_uri = ISNI[isni]
                g.add((uri, id_prop, isni_uri))
            elif f['2'] == 'orcid':
                orcid = f['a'].replace(' ', '')
                orcid_uri = URIRef(orcid)
                g.add((uri, id_prop, orcid_uri))
            elif f['2'] == 'viaf':
                viaf = f['a'].replace(' ', '')
                viaf_uri = VIAF[viaf]
                g.add((uri, id_prop, viaf_uri))
        
        # dates
        if '046' in rec:
            fld = rec['046']
            if 'f' in fld:
                g.add((uri, birthYear, Literal(str(fld['f'])[:4])))
            if 'g' in fld:
                g.add((uri, deathYear, Literal(str(fld['g'])[:4])))
            if 'q' in fld:
                g.add((uri, dateOfEstablishment, Literal(str(fld['q'])[:4])))
            if 'r' in fld:
                g.add((uri, dateOfTermination, Literal(str(fld['r'])[:4])))
            if 's' in fld or 't' in fld:
                # period of activity - encode as EDTF
                if 's' in fld:
                    start = str(fld['s'])[:4]
                else:
                    start = '..'

                if 't' in fld:
                    end = str(fld['t'])[:4]
                else:
                    end = '..'

                if is_person:
                    prop = periodOfActivityOfPerson
                else:
                    prop = periodOfActivityOfCorporateBody

                g.add((uri, prop, Literal('{}/{}'.format(start,end), datatype=EDTF)))

        for f in rec.get_fields('368'):
            if 'a' in f:
                prop = typeOfCorporateBody
                val = f['a']
            elif 'b' in f:
                prop = categoryOfGovernment
                val = f['b']
            elif 'c' in f:
                if is_person:
                    prop = otherDesignationAssociatedWithPerson
                else:
                    prop = otherDesignationAssociatedWithCorporateBody
                val = f['c']
            elif 'd' in f:
                prop = titleOfPerson
                val = f['d']
            else:
                logging.warning("Could not parse 368 value for <%s>, skipping", uri)
                continue

            obj = Literal(normalize(val), lang='fi') # by default, use a literal value
            if '0' in f:
                # use a URI value given in subfield 0 (likely from MTS) instead
                obj = URIRef(f['0'])
            elif '2' in f and f['2'] == 'mts':
                # see if we can find a URI value from MTS
                mtsuri = lookup_mts(val)
                if mtsuri is not None:
                    obj = mtsuri

            g.add((uri, prop, obj))

        for f in rec.get_fields('370'):
            if 'a' in f:
                place = lookup_yso_place(f['a'])
                g.add((uri, placeOfBirth, place))

            if 'b' in f:
                place = lookup_yso_place(f['b'])
                g.add((uri, placeOfDeath, place))

            if 'c' in f:
                place = lookup_yso_place(f['c'])
                
                if is_person:
                    prop = countryAssociatedWithPerson
                else:
                    prop = placeAssociatedWithCorporateBody

                g.add((uri, prop, place))

            if 'e' in f:
                place = lookup_yso_place(f['e'])

                if is_person:
                    prop = placeOfResidence
                else:
                    prop = placeAssociatedWithCorporateBody

                g.add((uri, prop, place))

            if 'f' in f:
                place = lookup_yso_place(f['f'])

                if is_person:
                    prop = placeAssociatedWithPerson
                else:
                    prop = placeAssociatedWithCorporateBody

                g.add((uri, prop, place))

        for f in rec.get_fields('372'):
            value = Literal(normalize(f.format_field()), lang='fi')
            if '0' in f:
                value = URIRef(f['0'])
            elif '2' in f and f['2'] == 'yso':
                ysouri = lookup_yso(f['a'])
                if ysouri:
                    value = ysouri

            if is_person:
                prop = fieldOfActivityOfPerson
            else:
                prop = fieldOfActivityOfCorporateBody

            g.add((uri, prop, value))

        for f in rec.get_fields('373'):
            for val in f.get_subfields('a'):
                g.add((uri, isPersonMemberOfCorporateBody, Literal(normalize(val), lang='fi')))

        for f in rec.get_fields('374'):
            value = Literal(normalize(f.format_field()), lang='fi')
            if '0' in f:
                value = URIRef(f['0'])
            elif '2' in f and f['2'] == 'mts':
                mtsuri = lookup_mts(f['a'])
                if mtsuri:
                    value = mtsuri

            g.add((uri, professionOrOccupation, value))

        for f in rec.get_fields('377'):
            for lang in f.get_subfields('a'):
                lang_uri = lookup_language(lang)
                if not lang_uri:
                    logging.warning("Unknown 377 language value '%s' for <%s>, skipping", lang, uri)
                    continue

                if is_person:
                    prop = languageOfPerson
                else:
                    prop = languageOfCorporateBody
                g.add((uri, prop, lang_uri))

        for f in rec.get_fields('378'):
            g.add((uri, fullerFormOfName, Literal(normalize(f.format_field()), lang='fi')))

        for f in rec.get_fields('400'):
            varname = format_label(f)
            if varname is None:
                logging.warning("Empty 400 value for <%s>, skipping", uri)
                continue
            varlit = Literal(varname, 'fi')
            g.add((uri, SKOS.altLabel, varlit))
            g.add((uri, variantNameOfPerson, varlit))

        for f in rec.get_fields('410') + rec.get_fields('411'):
            varname = format_label(f)
            if varname is None:
                logging.warning("Empty 410/411 value for <%s>, skipping", uri)
                continue
            varlit = Literal(varname, 'fi')
            g.add((uri, SKOS.altLabel, varlit))
            g.add((uri, variantNameOfCorporateBody, varlit))

        for f in rec.get_fields('500'):
            if is_person:
                prop = relatedPersonOfPerson  # default relationship
                if 'w' in f and f['w'] == 'r' and 'i' in f:
                    term = normalize_relterm(f['i'])
                    if term in rel500i:
                        prop = rel500i[term]
            else:
                prop = relatedPersonOfCorporateBody

            if '0' in f and f['0'].startswith('(FI-ASTERI-N)'):  # has ID, use it
                target_recid = f['0'].replace('(FI-ASTERI-N)', '')
                target = FINAF[target_recid]
            else:  # no ID - use a literal value for now
                logging.debug("Using literal value for <%s> 500", uri)
                target = Literal(format_label(f), lang='fi')
            g.add((uri, prop, target))

        for f in rec.get_fields('510') + rec.get_fields('511'):
            if is_person:
                prop = relatedCorporateBodyOfPerson
            else:
                prop = relatedCorporateBodyOfCorporateBody  # default relationship
                if 'w' in f:
                    if f['w'] == 'a':
                        prop = predecessor
                    elif f['w'] == 'b':
                        prop = successor
                    elif f['w'] == 't':
                        prop = hierarchicalSuperior
                    elif f['w'] == 'r':
                        if 'i' in f:
                            term = normalize_relterm(f['i'])
                            if term in rel510i:
                                prop = rel510i[term]
                    else:
                        logging.warning("Unknown 51X $w value for <%s>: %s", uri, f['w'])

            if '0' in f and f['0'].startswith('(FI-ASTERI-N)'):  # has ID, use it
                target_recid = f['0'].replace('(FI-ASTERI-N)', '')
                target = FINAF[target_recid]
            else:  # no ID - use a literal value for now
                logging.debug("Using literal value for <%s> 51X", uri)
                target = Literal(format_label(f), lang='fi')
            g.add((uri, prop, target))

        for f in rec.get_fields('670'):
            if 'u' in f: # has URL - try to build a link
                if 'a' in f:
                    if ', katsottu' in f['a']:
                        srcname, delim, rest = f['a'].partition(', katsottu')
                        link = "<a href='{}'>{}</a>{}{}".format(f['u'], srcname, delim, rest)
                    elif ', luettu' in f['a']:
                        srcname, delim, rest = f['a'].partition(', luettu')
                        link = "<a href='{}'>{}</a>{}{}".format(f['u'], srcname, delim, rest)
                    else:
                        link = "<a href='{}'>{}</a>".format(f['u'], f['a'])
                else: # only a URL without explanation
                    link = "<a href='{}'>{}</a>".format(f['u'], f['u'])

                if 'b' in f:
                    text = link + " " + f['b']
                else:
                    text = link
            else:
                text = f.format_field()

            g.add((uri, sourceConsulted, Literal(normalize(text), lang='fi')))

        for f in rec.get_fields('678'):
            if is_person:
                prop = biographicalInformation
            else:
                prop = corporateHistory

            g.add((uri, prop, Literal(normalize(f.format_field()), lang='fi')))

        for f in rec.get_fields('680'):
            if is_person:
                prop = noteOnPerson
            else:
                prop = noteOnCorporateBody

            g.add((uri, prop, Literal(normalize(f.format_field()), lang='fi')))

    # Pass 2: convert literal values to resources
    for prop in literal_to_resource:
        for s,o in g.subject_objects(prop):
            if not isinstance(o, Literal):
                continue
            resource = label_to_uri.get(str(o))
            if not resource:
                logging.warning("no resource found for '%s' (subject <%s>)", str(o), s)
            else:
                logging.debug("converting literal '%s' to resource '%s' (subject <%s>)", str(o), resource, s)
                g.remove((s, prop, o))
                g.add((s, prop, resource))

    # serialize output RDF as Turtle
    g.serialize(destination=sys.stdout.buffer, format='turtle')

if __name__ == '__main__':
    main()
