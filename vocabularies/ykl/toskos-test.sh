#!/bin/sh

RAWFILE="ykl-test.rdf"

SKOSIFYCMD="skosify"

INFILES="ykl-metadata.ttl ykl-hklj.ttl"
OUTFILE=ykl-test-skos.ttl

LOGFILE=skosify-test.log
OPTS="-c ykl.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --label YKL --mark-top-concepts"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
