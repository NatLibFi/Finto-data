#!/bin/sh

INFILES="ykl-metadata.ttl ykl.ttl ykl-hklj.ttl"
OUTFILE=ykl-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:ykl: --mark-top-concepts"


$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
