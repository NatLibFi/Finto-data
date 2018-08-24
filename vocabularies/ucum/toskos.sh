#!/bin/sh

INFILES="ucum-metadata.ttl ucum.ttl"
OUTFILE=ucum-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:ucum: --mark-top-concepts"
#-c udcs.cfg

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
