#!/usr/bin/env python

# Adds mappings and hierarchy from PNR to YSA

# Inputs:
# arg1: YSA SKOS (Turtle)
# arg2: YSA-PNR mappings (Turtle)

# Outputs:
# stdout: More triples for YSA (Turtle)
# stderr: warnings and error messages

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

import sys
import logging
import time

SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
YSA=Namespace('http://www.yso.fi/onto/ysa/')
LDFPNR=Namespace('http://ldf.fi/pnr/')
MMLPNR=Namespace('http://paikkatiedot.fi/so/1000772/')
PNR=Namespace('http://paikkatiedot.fi/def/1001010/pnr#')
SUBREG=Namespace('http://paikkatiedot.fi/def/1001010/Seutukunta#')
REGION=Namespace('http://paikkatiedot.fi/def/1001010/Suuralue#')
SCALE=Namespace('http://paikkatiedot.fi/def/1001010/Mittakaavarelevanssi#')

finland = YSA.Y94426

# initialize logging
logformat = '%(levelname)s: %(message)s'
loglevel = logging.DEBUG
logging.basicConfig(format=logformat, level=loglevel)        

logging.info("loading PNR ontology (type definitions etc.)")
pnront = Graph()
pnront.parse('http://paikkatiedot.fi/def/1001010/pnr#', format='xml')

logging.info("loading mappings")
mappings = Graph()
mappings.parse(sys.argv[2], format='turtle')

logging.info("loading YSA")
ysa = Graph()
ysa.parse(sys.argv[1], format='turtle')

# create output graph
out = Graph()
out.bind('skos', SKOS)
out.bind('ysa', YSA)

# add "Suomi" label to assist MARC record updating
out.add((finland, SKOS.prefLabel, Literal("Suomi", "fi")))

def ldf_to_pnr_uri(ldf_uri):
    if LDFPNR['P_'] in ldf_uri:
        return URIRef(ldf_uri.replace(LDFPNR['P_'],MMLPNR))
    elif LDFPNR['subregion_'] in ldf_uri:
        return URIRef(ldf_uri.replace(LDFPNR['subregion_'],SUBREG['c']))
    elif LDFPNR['large_area_'] in ldf_uri:
        return URIRef(ldf_uri.replace(LDFPNR['large_area_'],REGION['c']))
    else:
        logging.critical("Cannot convert LDF URI <%s> to PNR equivalent", ldf_uri)
        return None

def pnr_to_ldf_uri(pnr_uri):
    if MMLPNR in pnr_uri:
        return URIRef(pnr_uri.replace(MMLPNR, LDFPNR['P_']))
    elif SUBREG['c'] in pnr_uri:
        return URIRef(pnr_uri.replace(SUBREG['c'], LDFPNR['subregion_']))
    else:
        logging.critical("Cannot convert PNR URI <%s> to LDF equivalent", pnr_uri)
        return None
        
def scaleuri_to_value(scaleuri):
    return int(scaleuri.replace(SCALE['c'], ''))

logging.info("Adding PNR mappings and hierarchy...")
count = 0
for ysauri, target in mappings.subject_objects(SKOS.closeMatch):
    logging.info("---")
    try:
        ysalabel = ysa.preferredLabel(ysauri)[0][1]
    except IndexError:
        logging.warning("YSA URI <%s> has disappeared, skipping", ysauri)
        continue
    pnruri = ldf_to_pnr_uri(target)
    logging.info("YSA: <%s> '%s'", ysauri, ysalabel)
    out.add((ysauri, SKOS.prefLabel, Literal(ysalabel, 'fi')))
    pnrdata = Graph()
    starttime = time.time()
    pnrdata.parse(pnruri, format='xml')
    endtime = time.time()
    logging.debug('Loaded %d triples from %s in %.2f seconds', len(pnrdata), pnruri, endtime-starttime)
    try: # prefer Finnish
        pnrlabel = pnrdata.preferredLabel(pnruri,lang='fi')[0][1]
    except IndexError: # but any language will do
        try:
            pnrlabel = pnrdata.preferredLabel(pnruri)[0][1]
        except IndexError:
            logging.warning("Fetching PNR labels from <%s> failed, aborting.", pnruri)
            continue
    logging.info("PNR: <%s> '%s'", pnruri, pnrlabel)

    for pnrtype in pnrdata.objects(pnruri, RDF.type):
        try:
            typelabel = pnront.preferredLabel(pnrtype, lang='fi')[0][1]
        except IndexError: # it's not in the ontology - try the original data (regions)
            typelabel = pnrdata.preferredLabel(pnrtype, lang='fi')[0][1]
        logging.info("type: <%s> '%s'", pnrtype, typelabel)
        out.add((ysauri, RDF.type, pnrtype))
        out.add((pnrtype, RDFS.label, Literal(typelabel, 'fi')))
        out.add((ysauri, SKOS.closeMatch, pnruri))
        if pnrtype in (PNR.MunicipalityRuralArea, PNR.MunicipalityUrbanArea):
            subregion = pnrdata.value(pnruri, PNR.seutukunta, None)
            logging.info("adding subregion <%s> as RT", subregion)
            ysa_subregion = mappings.value(None, SKOS.closeMatch, pnr_to_ldf_uri(subregion))
            if ysa_subregion is not None:
                ysa_subreg_label = ysa.preferredLabel(ysa_subregion)[0][1]
                logging.info("YSA subregion: <%s> '%s'", ysa_subregion, ysa_subreg_label)
                out.add((ysauri, SKOS.related, ysa_subregion))
                out.add((ysa_subregion, SKOS.related, ysauri))
                out.add((ysa_subregion, SKOS.prefLabel, Literal(ysa_subreg_label, 'fi')))
            else:
                logging.warning("No equivalent subregion for <%s> found in YSA, skipping", subregion)

            region = pnrdata.value(pnruri, PNR.inRegion, None)
            logging.info("adding region <%s> as BT", region)
            ysa_region = mappings.value(None, SKOS.closeMatch, pnr_to_ldf_uri(region))
            if ysa_region is None:
                logging.warning("No equivalent region for <%s> found in YSA, skipping", region)
                continue
            ysa_region_label = ysa.preferredLabel(ysa_region)[0][1]
            logging.info("YSA region: <%s> '%s'", ysa_region, ysa_region_label)
            out.add((ysauri, SKOS.broader, ysa_region))
            out.add((ysa_region, SKOS.narrower, ysauri))
            if ysa_subregion is not None:
                logging.info("adding YSA subregion <%s> as NT to YSA region <%s>", ysa_subregion, ysa_region)
                out.add((ysa_subregion, SKOS.broader, ysa_region))
                out.add((ysa_region, SKOS.narrower, ysa_subregion))
            out.add((ysa_region, SKOS.prefLabel, Literal(ysa_region_label, 'fi')))
        elif pnrtype in (PNR.Region, PNR.Province, URIRef('http://paikkatiedot.fi/def/1001010/Suuralue')):
            logging.info("adding Suomi as BT")
            out.add((ysauri, SKOS.broader, finland))
            out.add((finland, SKOS.narrower, ysauri))
        elif pnrtype == URIRef('http://paikkatiedot.fi/def/1001010/Seutukunta'):
            logging.info("Not adding BT for subregion.")
        else:
            if pnrtype in (PNR.SeaLakeOrPond, PNR.Watercourse, PNR.PartOfSeaLakeOrPond):
                scale = scaleuri_to_value(pnrdata.value(pnruri, PNR.mittakaavarelevanssi, None))
                logging.info("scale: %d", scale)
                if scale >= 2000000:
                    logging.info("not adding municipality as BT")
                    continue
            municipality = pnrdata.value(pnruri, PNR.inMunicipalityRuralArea, None)
            if municipality is None:
                municipality = pnrdata.value(pnruri, PNR.inMunicipalityUrbanArea, None)
            logging.info("adding municipality <%s> as BT", municipality)
            ysa_municipality = mappings.value(None, SKOS.closeMatch, pnr_to_ldf_uri(municipality))
            ysa_munic_label = ysa.preferredLabel(ysa_municipality)[0][1]
            logging.info("YSA municipality: <%s> '%s'", ysa_municipality, ysa_munic_label)
            out.add((ysauri, SKOS.broader, ysa_municipality))
            out.add((ysa_municipality, SKOS.narrower, ysauri))
            out.add((ysa_municipality, SKOS.prefLabel, Literal(ysa_munic_label, 'fi')))
            
                
            
    count += 1
#    if count == 500: break

logging.info("Adding editorial notes...")

for ysauri, note in mappings.subject_objects(SKOS.editorialNote):
    out.add((ysauri, SKOS.editorialNote, note))

logging.info("All done.")

out.serialize(destination=sys.stdout, format='turtle')
