#!/bin/sh

INFILES="cer-metadata.ttl cer.ttl"
OUTFILE=cer-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://tieteentermipankki.fi/wiki/ --mark-top-concepts"
#-c cer.cfg

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
