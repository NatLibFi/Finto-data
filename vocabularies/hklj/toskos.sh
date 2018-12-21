#!/bin/sh

INFILES="hklj-metadata.ttl hklj.ttl"
OUTFILE=hklj-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:hklj: --mark-top-concepts"


$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
