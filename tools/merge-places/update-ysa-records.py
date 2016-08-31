#!/usr/bin/env python

# Updates YSA MARC records with links to Paikannimirekisteri

# Inputs:
# arg1: YSA MARC records (marc21 binary format)
# arg2: YSA-PNR mappings (Turtle)

# Outputs:
# stdout: Modified YSA MARC records (marc21 binary format)
# stderr: warnings and error messages

from pymarc import MARCReader, Field
from rdflib import Graph, Namespace, URIRef, RDF, RDFS

import sys

SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
YSA=Namespace('http://www.yso.fi/onto/ysa/')
LDFPNR=Namespace('http://ldf.fi/pnr/')
MMLPNR=Namespace('http://paikkatiedot.fi/so/1000772/')

# load PNR ontology (type definitions etc.)
pnront = Graph()
pnront.parse('http://paikkatiedot.fi/def/1001010/pnr#', format='xml')

# load mappings
mappings = Graph()
mappings.parse(sys.argv[2], format='turtle')

def ldf_to_pnr_uri(ldf_uri):
    return URIRef(ldf_uri.replace(LDFPNR + 'P_',MMLPNR))

def ysa_uri(recid):
    return YSA['Y'+recid]

with open(sys.argv[1], 'rb') as fh:
    reader = MARCReader(fh)
    for rec in reader:
        changed = False
        recid = rec['001'].value()
        uri = ysa_uri(recid)
        print >>sys.stderr, ""
        print >>sys.stderr, uri
        for target in mappings.objects(uri, SKOS.closeMatch):
            pnruri = ldf_to_pnr_uri(target)
            print >>sys.stderr, "match:", pnruri
            pnrdata = Graph()
            pnrdata.parse(pnruri, format='xml')
            for pnrtype in pnrdata.objects(pnruri, RDF.type):
                print >>sys.stderr, "type:", pnrtype
                typelabel = pnront.preferredLabel(pnrtype, lang='fi')[0][1]
                print >>sys.stderr, "type label:", typelabel
                rec.add_field(
                    Field(
                        tag='670',
                        indicators = [' ', ' '],
                        subfields = [
                            'a', 'Maanmittauslaitoksen paikannimirekisteri',
                            'b', 'tyyppitieto: %s' % typelabel,
                            'u', pnruri
                        ]))
                changed = True
        if changed:
            sys.stdout.write(rec.as_marc())
