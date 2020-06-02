#!/usr/bin/env python3

import sys
import io
import functools

import requests
import pymarc.marcxml
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
OWL=Namespace("http://www.w3.org/2002/07/owl#")
DC=Namespace("http://purl.org/dc/elements/1.1/")
DCT=Namespace("http://purl.org/dc/terms/")
RDAA=Namespace("http://rdaregistry.info/Elements/a/")
RDAC=Namespace("http://rdaregistry.info/Elements/c/")
XSD=Namespace("http://www.w3.org/2001/XMLSchema#")
ISNI=Namespace("http://isni.org/isni/")
FINAF=Namespace("http://urn.fi/URN:NBN:fi:au:finaf:")

# mnemonics for RDA URIs
Person=RDAC.C10004
CorporateBody=RDAC.C10005
preferredNameOfPerson=RDAA.P50117
preferredNameOfCorporateBody=RDAA.P50041
birthYear=RDAA.P50121
deathYear=RDAA.P50120
typeOfCorporateBody=RDAA.P50237
categoryOfGovernment=RDAA.P50238
otherDesignationAssociatedWithPerson=RDAA.P50108
otherDesignationAssociatedWithCorporateBody=RDAA.P50033
titleOfPerson=RDAA.P50110

FINTO_API_BASE="http://api.finto.fi/rest/v1/"

def initialize_graph():
    g = Graph()
    g.namespace_manager.bind('skos', SKOS)
    g.namespace_manager.bind('finaf', FINAF)
    g.namespace_manager.bind('dc', DC)
    g.namespace_manager.bind('dct', DCT)
    g.namespace_manager.bind('rdaa', RDAA)
    g.namespace_manager.bind('rdac', RDAC)
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
    payload = {'label': label, 'lang': 'fi'}
    req = requests.get(FINTO_API_BASE + 'mts/lookup', params=payload)
    if req.status_code != 200:
        return None

    return URIRef(req.json()['result'][0]['uri'])

def main():
    g = initialize_graph()

    for line in sys.stdin:
        file = io.StringIO(line)
        rec = pymarc.marcxml.parse_xml_to_array(file)[0]
        
        # sanity check
        if '100' not in rec and '110' not in rec and '111' not in rec:
            continue
        
        id = rec['001'].value()
        uri = FINAF[id]

        if '100' in rec: # person name
            # don't include living persons for now
            if '046' not in rec:
                continue  # no information about birth/death years
            if 'g' not in rec['046']:
                continue  # death year not set
        
            g.add((uri, RDF.type, Person))
            label = format_label(rec['100'])
            labelprop = preferredNameOfPerson
            is_person = True
        else: # corporate or meeting names
            g.add((uri, RDF.type, CorporateBody))
            f = rec.get_fields('110', '111')[0]
            label = format_label(f)
            labelprop = preferredNameOfCorporateBody
            is_person = False
        g.add((uri, RDF.type, SKOS.Concept))
        literal = Literal(label, lang='fi') # prefLabel is always Finnish
        g.add((uri, SKOS.prefLabel, literal))
        g.add((uri, labelprop, literal))
        
        # created timestamp
        created = rec['008'].value()[:6]
        g.add((uri, DCT.created, Literal(format_timestamp(created), datatype=XSD.date)))

        # modified timestamp
        modified = rec['005'].value()[2:14] # FIXME ugly...discards century info
        g.add((uri, DCT.modified, Literal(format_timestamp(modified), datatype=XSD.dateTime)))

        # ISNI
        for f in rec.get_fields('024'):
            if '2' in f and f['2'] == 'isni' and 'a' in f:
                isni = ISNI[f['a'].replace(' ', '')]
                g.add((uri, SKOS.closeMatch, isni))
        
        # birth and death years
        if '046' in rec:
            fld = rec['046']
            if 'f' in fld:
                g.add((uri, birthYear, Literal(str(fld['f'])[:4], datatype=XSD.gYear, normalize=False)))
            if 'g' in fld:
                g.add((uri, deathYear, Literal(fld['g'][:4], datatype=XSD.gYear, normalize=False)))

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
                print("Could not parse 368 value for <%s>, skipping" % uri, file=sys.stderr)
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

    # serialize output RDF as Turtle
    g.serialize(destination=sys.stdout.buffer, format='turtle')

if __name__ == '__main__':
    main()
