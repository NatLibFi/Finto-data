#!/bin/sh

EXPANDURIS="../../tools/expand-note-uris/expand-note-uris.py"

# fetch mappings from Wikidata and store them in a sorted NT file, so version control works
rsparql --results NT --service https://query.wikidata.org/sparql --query wikidata-links.rq | sort >wikidata-links.nt

# convert wkt literals into wgs84 lat/long
./wkt2wgs84.py < wikidata-links.nt > wikidata-links-single-value-coordinates.ttl

# grep used PNR places (their paikkaIDs)
grep -oP "(?<=rdf:resource=\"http://paikkatiedot.fi/so/1000772/).*(?=\")" yso-paikat-vb-dump.rdf | sort -u > yso-paikat-usedPNRs.txt

# create wgs84 lat/long literals for used PNR places
./extractUsedPNRs.py --input pnr-complete-paikkaid-wgs84-coordinates-table-2020-12-02.csv --selector yso-paikat-usedPNRs.txt > yso-paikat-pnr.ttl

# expand URIs in notes and definitions
$EXPANDURIS yso-paikat-vb-dump.ttl >yso-paikat-expanded.ttl 2>yso-paikat-expanded.log

INFILES="yso-paikat-expanded.rdf yso-paikat-pnr.ttl wikidata-links-single-value-coordinates.ttl yso-paikat-metadata.ttl"
OUTFILE=yso-paikat-skos.ttl
CFGFILE=yso-paikat-vb.cfg

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings --set-modified --namespace http://www.yso.fi/onto/yso/"

$SKOSIFYCMD -c $CFGFILE $OPTS $INFILES -o $OUTFILE 2>$LOGFILE

#Uudenmalliselle YSO-paikoille ei ole testejä. Vielä.
#bats test.bats
