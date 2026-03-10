#!/bin/sh

SKOSIFYCMD="skosify"
INFILES="yse-test-metadata.ttl yse-test.ttl"
OUTFILE=yse-test-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-mark-top-concepts --no-enrich-mappings --no-aggregates -F turtle"

$SKOSIFYCMD $OPTS $INFILES >$OUTFILE 2>$LOGFILE
