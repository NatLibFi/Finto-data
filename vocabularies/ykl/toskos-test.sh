#!/bin/sh

SKOSIFYCMD="skosify"

INFILES="ykl-test.rdf ykl-metadata.ttl ykl-hklj.ttl"
OUTFILE=ykl-test-skos.ttl

LOGFILE=skosify-test.log
OPTS="-c ykl-test.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --label YKL --mark-top-concepts"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
