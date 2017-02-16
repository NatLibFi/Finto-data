#!/bin/sh

INFILES="iptc-metadata.ttl iptc-subjectcode-fi.ttl scene-cptall-en-GB.rdf subjectcode-cptall-en-GB.rdf"
OUTFILE=iptc-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings --update-query=@add-notations.ru"

./csv-to-skos.py iptc_v2_1.csv >iptc-subjectcode-fi.ttl
$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
