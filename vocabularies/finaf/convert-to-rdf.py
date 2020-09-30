#!/usr/bin/env python3

import sys
import io
import functools
import logging

import requests
import pymarc.marcxml
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, BNode
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
alternateIdentity=RDAA.P50428
realIdentity=RDAA.P50429
relatedCorporateBodyOfPerson=RDAA.P50318
relatedCorporateBodyOfCorporateBody=RDAA.P50218
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
LITERAL_TO_RESOURCE = (
    isPersonMemberOfCorporateBody,
    alternateIdentity,
    realIdentity,
    relatedPersonOfPerson,
    relatedPersonOfCorporateBody,
    relatedCorporateBodyOfPerson,
    relatedCorporateBodyOfCorporateBody,
    predecessor,
    successor,
    hierarchicalSuperior
)

nameOfPlace=RDAP.P70001

EDTF=URIRef('http://id.loc.gov/datatypes/edtf')

FINTO_API_BASE="http://api.finto.fi/rest/v1/"
FINTO_SPARQL_ENDPOINT="http://api.finto.fi/sparql"

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
    logging.debug('looking up YSO place "%s"', label)
    if ', ' in label:
        place, country = label.rsplit(', ', 1)
        country_uri = lookup_yso_place(country)
        if isinstance(country_uri, BNode):
            logging.debug('YSO place lookup for country "%s" failed', country)
            return BNode()
        payload = {'query': place, 'parent': str(country_uri), 'lang': 'fi'}
        req = requests.get(FINTO_API_BASE + 'yso-paikat/search', params=payload)
        if req.status_code != 200:
            logging.debug('YSO place lookup for place "%s" failed (error)', place)
            return BNode()
        results = req.json()['results']
        if results:
            return URIRef(results[0]['uri'])
        logging.debug('YSO place lookup for place "%s" failed (no results)', place)
        return BNode()

    payload = {'label': label, 'lang': 'fi'}
    req = requests.get(FINTO_API_BASE + 'yso-paikat/lookup', params=payload)
    if req.status_code != 200:
        logging.debug('YSO place lookup for place "%s" failed', label)
        return BNode()

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

    # Pass 1: convert MARC data to basic RDF
    for line in sys.stdin:
        file = io.StringIO(line)
        rec = pymarc.marcxml.parse_xml_to_array(file)[0]
        
        recid = rec['001'].value()
        uri = FINAF[recid]

        logging.info("Starting conversion of record %s", recid)

        # sanity check
        if '100' not in rec and '110' not in rec and '111' not in rec:
            logging.warning('no 100/110/111 field, skipping record %s', rec['001'].value())
            continue
        
        if '100' in rec: # person name
            # don't include living persons for now
            if '046' not in rec:
                logging.debug('skipping person record without 046 field')
                continue  # no information about birth/death years
            if 'g' not in rec['046']:
                logging.debug('skipping person record without death year in 046')
                continue  # death year not set
        
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

        # ISNI & ORCID iD
        for f in rec.get_fields('024'):
            if is_person:
                prop = identifierForPerson
            else:
                prop = identifierForCorporateBody

            if '2' in f and f['2'] == 'isni' and 'a' in f:
                isni = f['a'].replace(' ', '')
                isni_uri = ISNI[isni]
                label = Literal("ISNI {} {} {} {}".format(isni[:4], isni[4:8], isni[8:12], isni[12:]))
                g.add((uri, prop, isni_uri))
                g.add((isni_uri, RDFS.label, label))
            if '2' in f and f['2'] == 'orcid' and 'a' in f:
                orcid = f['a'].replace(' ', '')
                orcid_uri = URIRef(orcid)
                label = Literal("ORCID iD {}".format(orcid))
                g.add((uri, prop, orcid_uri))
                g.add((orcid_uri, RDFS.label, label))
        
        # dates
        if '046' in rec:
            fld = rec['046']
            if 'f' in fld:
                g.add((uri, birthYear, Literal(str(fld['f'])[:4], datatype=XSD.gYear, normalize=False)))
            if 'g' in fld:
                g.add((uri, deathYear, Literal(str(fld['g'])[:4], datatype=XSD.gYear, normalize=False)))
            if 'q' in fld:
                g.add((uri, dateOfEstablishment, Literal(str(fld['q'])[:4], datatype=XSD.gYear, normalize=False)))
            if 'r' in fld:
                g.add((uri, dateOfTermination, Literal(str(fld['r'])[:4], datatype=XSD.gYear, normalize=False)))
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

            obj = Literal(val, lang='fi') # by default, use a literal value
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
                if isinstance(place, BNode):
                    g.add((place, nameOfPlace, Literal(f['a'], lang='fi')))
                    g.add((place, SKOS.prefLabel, Literal(f['a'], lang='fi')))

            if 'b' in f:
                place = lookup_yso_place(f['b'])
                g.add((uri, placeOfDeath, place))
                if isinstance(place, BNode):
                    g.add((place, nameOfPlace, Literal(f['b'], lang='fi')))
                    g.add((place, SKOS.prefLabel, Literal(f['b'], lang='fi')))

            if 'c' in f:
                place = lookup_yso_place(f['c'])
                g.add((uri, countryAssociatedWithPerson, place))
                if isinstance(place, BNode):
                    g.add((place, nameOfPlace, Literal(f['c'], lang='fi')))
                    g.add((place, SKOS.prefLabel, Literal(f['c'], lang='fi')))

            if 'e' in f:
                place = lookup_yso_place(f['e'])

                if is_person:
                    prop = placeOfResidence
                else:
                    prop = placeAssociatedWithCorporateBody

                g.add((uri, prop, place))
                if isinstance(place, BNode):
                    g.add((place, nameOfPlace, Literal(f['e'], lang='fi')))
                    g.add((place, SKOS.prefLabel, Literal(f['e'], lang='fi')))

            if 'f' in f:
                place = lookup_yso_place(f['f'])

                if is_person:
                    prop = placeAssociatedWithPerson
                else:
                    prop = placeAssociatedWithCorporateBody

                g.add((uri, prop, place))
                if isinstance(place, BNode):
                    g.add((place, nameOfPlace, Literal(f['f'], lang='fi')))
                    g.add((place, SKOS.prefLabel, Literal(f['f'], lang='fi')))

        for f in rec.get_fields('372'):
            value = Literal(f.format_field(), lang='fi')
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
                g.add((uri, isPersonMemberOfCorporateBody, Literal(val, lang='fi')))

        for f in rec.get_fields('374'):
            value = Literal(f.format_field(), lang='fi')
            if '0' in f:
                value = URIRef(f['0'])
            elif '2' in f and f['2'] == 'mts':
                mtsuri = lookup_mts(f['a'])
                if mtsuri:
                    value = mtsuri

            g.add((uri, professionOrOccupation, value))

        for f in rec.get_fields('377'):
            if 'a' in f:
                lang_uri = lookup_language(f['a'])
                if not lang_uri:
                    logging.warning("Unknown 377 language value '%s' for <%s>, skipping", f['a'], uri)
                    continue

                if is_person:
                    prop = languageOfPerson
                else:
                    prop = languageOfCorporateBody
                g.add((uri, prop, lang_uri))

        for f in rec.get_fields('378'):
            g.add((uri, fullerFormOfName, Literal(f.format_field(), lang='fi')))

        for f in rec.get_fields('400'):
            varname = format_label(f)
            if varname is None:
                logging.warning("Empty 400 value for <%s>, skipping", uri)
                continue
            varlit = Literal(varname)
            g.add((uri, SKOS.altLabel, varlit))
            g.add((uri, variantNameOfPerson, varlit))

        for f in rec.get_fields('410') + rec.get_fields('411'):
            varname = format_label(f)
            if varname is None:
                logging.warning("Empty 410/411 value for <%s>, skipping", uri)
                continue
            varlit = Literal(varname)
            g.add((uri, SKOS.altLabel, varlit))
            g.add((uri, variantNameOfCorporateBody, varlit))

        for f in rec.get_fields('500'):
            if is_person:
                prop = relatedPersonOfPerson  # default relationship
                if 'w' in f and f['w'] == 'r' and 'i' in f:
                    if f['i'].startswith('Toinen identiteetti'):
                        prop = alternateIdentity
                    elif f['i'].startswith('Todellinen identiteetti'):
                        prop = realIdentity
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

            g.add((uri, sourceConsulted, Literal(text, lang='fi')))

        for f in rec.get_fields('678'):
            if is_person:
                prop = biographicalInformation
            else:
                prop = corporateHistory

            g.add((uri, prop, Literal(f.format_field(), lang='fi')))

        for f in rec.get_fields('680'):
            if is_person:
                prop = noteOnPerson
            else:
                prop = noteOnCorporateBody

            g.add((uri, prop, Literal(f.format_field(), lang='fi')))

    # Pass 2: convert literal values to resources
    for prop in LITERAL_TO_RESOURCE:
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
