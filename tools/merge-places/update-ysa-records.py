#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Updates YSA MARC records with links to Paikannimirekisteri

# Inputs:
# arg1: YSA MARC records (marc21 binary format)
# arg2: YSA with enrichments (Turtle)

# Outputs:
# stdout: Modified YSA MARC records (marc21 binary format)
# stderr: warnings and error messages

from pymarc import MARCReader, Field
from rdflib import Graph, Namespace, URIRef, RDF, RDFS

import sys
import logging

SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
YSA=Namespace('http://www.yso.fi/onto/ysa/')
LDFPNR=Namespace('http://ldf.fi/pnr/')
MMLPNR=Namespace('http://paikkatiedot.fi/so/1000772/')
PNR=Namespace('http://paikkatiedot.fi/def/1001010/pnr#')
SUBREG=Namespace('http://paikkatiedot.fi/def/1001010/Seutukunta#')

# initialize logging
logformat = '%(levelname)s: %(message)s'
loglevel = logging.DEBUG
logging.basicConfig(format=logformat, level=loglevel)        


# load enriched YSA
enriched = Graph()
enriched.parse(sys.argv[2], format='turtle')

def ysa_uri(recid):
    return YSA['Y'+recid]

def remove_existing_551(rec, label):
    for fld in rec.get_fields('551'):
        oldlabel = fld['a']
        if 'z' in fld:
            oldlabel += " -- " + fld['z']
        if oldlabel == unicode(label):
            logging.info("Removing existing 551 '%s'", fld.format_field())
            rec.remove_field(fld)

def label_to_subfields(label):
    if ' -- ' in label:
        a,z = label.split(' -- ')
        return ['a', a, 'z', z]
    else:
        return ['a', label]

with open(sys.argv[1], 'rb') as fh:
    reader = MARCReader(fh)
    for rec in reader:
        changed = False
        recid = rec['001'].value()
        uri = ysa_uri(recid) # FIXME check 024
        logging.info("YSA URI: <%s>", uri)
        
        # check for BT relationships and add
        for broader in enriched.objects(uri, SKOS.broader):
            btlabel = enriched.preferredLabel(broader, lang='fi')[0][1]
            remove_existing_551(rec, btlabel)
            logging.info("BT: <%s> '%s'", broader, btlabel)
            rec.add_ordered_field(
                Field(
                    tag='551',
                    indicators = [' ', ' '],
                    subfields = ['w', 'g'] + label_to_subfields(btlabel)
                    ))
            changed = True            
        
        # check for NT relationships and add
        for narrower in enriched.objects(uri, SKOS.narrower):
            ntlabel = enriched.preferredLabel(narrower, lang='fi')[0][1]
            remove_existing_551(rec, ntlabel)
            logging.info("NT: <%s> '%s'", narrower, ntlabel)
            rec.add_ordered_field(
                Field(
                    tag='551',
                    indicators = [' ', ' '],
                    subfields = ['w', 'h'] + label_to_subfields(ntlabel)
                    ))
            changed = True            
        
        # check for RT relationships and add
        for related in enriched.objects(uri, SKOS.related):
            rtlabel = enriched.preferredLabel(related, lang='fi')[0][1]
            remove_existing_551(rec, rtlabel)
            logging.info("RT: <%s> '%s'", related, rtlabel)
            rec.add_ordered_field(
                Field(
                    tag='551',
                    indicators = [' ', ' '],
                    subfields = label_to_subfields(rtlabel)
                    ))
            changed = True            
        
        # check for editorial notes and add
        for ednote in enriched.objects(uri, SKOS.editorialNote):
            logging.info("EdNote: '%s'", ednote)
            rec.add_ordered_field(
                Field(
                    tag='667',
                    indicators = [' ', ' '],
                    subfields = [
                        'a', u'PNR-linkitystä koskeva huomautus: %s' % ednote
                    ]))
            changed = True
        
        # check for mappings and add
        for pnruri in enriched.objects(uri, SKOS.closeMatch):
            logging.info("PNR mapping: <%s>", pnruri)
            for pnrtype in enriched.objects(pnruri, RDF.type):
                logging.info("PNR type: <%s>", pnrtype)
                typelabel = enriched.preferredLabel(pnrtype, lang='fi')[0][1]
                logging.info("PNR type label: '%s'", typelabel)
                rec.add_ordered_field(
                    Field(
                        tag='670',
                        indicators = [' ', ' '],
                        subfields = [
                            'a', 'Maanmittauslaitoksen paikannimirekisteri',
                            'b', 'tyyppitieto: %s' % typelabel,
                            'u', str(pnruri)
                        ]))
                changed = True
        if changed:
            sys.stdout.write(rec.as_marc())
