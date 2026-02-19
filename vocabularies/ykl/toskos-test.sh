#!/bin/sh

RAWFILE="ykl-test.ttl"

SKOSIFYCMD="skosify"

INFILES="ykl-metadata.ttl ykl-hklj.ttl"
OUTFILE=ykl-test-skos.ttl

LOGFILE=skosify-test.log
OPTS="-c ykl.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --mark-top-concepts"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
