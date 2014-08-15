#!/bin/sh

INFILES="iptc-subjectcode-metadata.ttl iptc-subjectcode-fi.ttl cptall-en-GB.rdf"
OUTFILE=iptc-subjectcode-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS=""

./csv-to-skos.py iptc_v2_1.csv >iptc-subjectcode-fi.ttl
$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
