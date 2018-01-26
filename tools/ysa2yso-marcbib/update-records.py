#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Updates Fennica MARC records, changing YSA concept references
# in 650 and 651 fields to corresponding YSO and YSO Place concepts

# Inputs:
# arg1: MARC records (marc21 binary format)
# arg2: YSA SKOS (Turtle)
# arg3: YSO SKOS (Turtle)
# arg4: YSO Places SKOS (Turtle)

# Outputs:
# stdout: Modified MARC records (marc21 binary format)
# stderr: warnings and error messages

from pymarc import MARCReader, Field
from rdflib import Graph, Namespace, Literal

import sys
import logging

SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
YSO=Namespace('http://www.yso.fi/onto/yso/')

if len(sys.argv) != 5:
    print("Usage: %s <input.mrc> <ysa-skos.ttl> <yso-skos.ttl> <yso-paikat-skos.ttl> >output.mrc" % sys.argv[0], file=sys.stderr)
    sys.exit(1)

# initialize logging
logformat = '%(levelname)s: %(message)s'
loglevel = logging.DEBUG
logging.basicConfig(format=logformat, level=loglevel)        

# load YSA
logging.info("Loading YSA from %s ...", sys.argv[2])
ysa = Graph()
ysa.parse(sys.argv[2], format='turtle')

# load YSO
logging.info("Loading YSO from %s ...", sys.argv[3])
yso = Graph()
yso.parse(sys.argv[3], format='turtle')

# load YSO Places
logging.info("Loading YSO Places from %s ...", sys.argv[4])
ysop = Graph()
ysop.parse(sys.argv[4], format='turtle')


def combined_label(f):
    labels = f.get_subfields('a', 'x', 'z')
    label = ' -- '.join(labels)
    return label

def ysalabel_to_ysauri(label):
    # prefLabel
    uri = ysa.value(None, SKOS.prefLabel, Literal(label, "fi"))
    if uri is not None:
        return uri
    # altLabel
    uri = ysa.value(None, SKOS.altLabel, Literal(label, "fi"))
    if uri is not None:
        return uri
    return None

def ysauri_to_ysouris(ysauri):
    if ysauri is None:
        return []
    return [uri for prop in (SKOS.closeMatch, SKOS.exactMatch)
                for uri in ysa.objects(ysauri, prop)
            if uri.startswith(YSO)]

def ysouri_label_ft(uri):
    for voc, ft in ((yso, '650'), (ysop, '651')):
        labels = voc.preferredLabel(uri, lang='fi')
        if len(labels) > 0:
            return (labels[0][1], ft)
    return (None, None)

with open(sys.argv[1], 'rb') as fh:
    reader = MARCReader(fh)
    count = 0
    for rec in reader:
        changed_fields = set()
        recid = rec['001'].value()
        
        for ftype in ('650','651'):
            for subjf in rec.get_fields(ftype):
                if '2' in subjf and subjf['2'] == 'ysa':
                    label = combined_label(subjf)
                    ysauri = ysalabel_to_ysauri(label)
                    logging.debug("%s YSA: %s <%s> '%s'", recid, ftype, ysauri, label)
                    if ysauri is None:
                        continue
                    ysouris = ysauri_to_ysouris(ysauri)
                    if len(ysouris) == 0:
                        continue
                    rec.remove_field(subjf)
                    changed_fields.add(ftype)
                    for ysouri in ysouris:
                        ysolabel, ysoft = ysouri_label_ft(ysouri)
                        if ysolabel is None:
                            logging.warning("No label found for YSO URI <%s>, skipping" % ysouri)
                            continue
                        if ysoft != ftype:
                            logging.warning("Field type mismatch: %s != %s", ftype, ysoft)
                        logging.debug("\t\tYSO: %s <%s> '%s'", ysoft, ysouri, ysolabel)
                        fld = Field(tag=ysoft,
                                    indicators=[' ','7'],
                                    subfields=[
                                        'a', ysolabel,
                                        '0', str(ysouri), # avoid "does not look like a valid URI" warnings
                                        '2', 'yso/fin'
                                    ])
                        rec.add_ordered_field(fld)
        for tag in changed_fields:
            logging.info('Sorting field %s', tag)
            fields = rec.get_fields(tag)
            rec.remove_fields(tag)
            fields.sort(key=lambda f:f.format_field())
            for f in fields:
                logging.info('field value: %s', f.format_field())
                rec.add_ordered_field(f)

        sys.stdout.buffer.write(rec.as_marc())
        count += 1

logging.info("Converted %d records", count)
