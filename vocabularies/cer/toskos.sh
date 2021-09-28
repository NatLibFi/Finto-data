#!/bin/sh

INFILES="cer-metadata.ttl cer.ttl"
OUTFILE=cer-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://tieteentermipankki.fi/wiki/ --mark-top-concepts"
#-c cer.cfg

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
