#!/bin/sh

# fetch mappings from Wikidata and store them in a sorted NT file, so version control works
rsparql --results NT --service https://query.wikidata.org/sparql --query wikidata-links.rq | sort >wikidata-links.nt

INFILES="yso-paikat-metadata.ttl yso-paikat-vb-dump.rdf wikidata-links.nt"
OUTFILE=yso-paikat-vb-skos.ttl
CFGFILE=ysopaikat-vb.cfg

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings --set-modified --namespace http://www.yso.fi/onto/yso/"

$SKOSIFYHOME/skosify.py -c $CFGFILE $INFILES -o $OUTFILE 2>$LOGFILE
