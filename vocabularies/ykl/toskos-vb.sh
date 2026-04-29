#!/bin/bash

# YKL:n VocBenchin testiversion julkaisukomennot

SKOSIFYCMD="skosify"

INFILES="ykl-metadata.ttl ykl-test.rdf ykl-hklj.ttl"
OUTFILE="ykl-test-skos.ttl"
LOGFILE="skosify-test.log"
OPTS="-c ykl-test.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --mark-top-concepts -F turtle"

$SKOSIFYCMD $OPTS $INFILES >$OUTFILE 2>$LOGFILE
