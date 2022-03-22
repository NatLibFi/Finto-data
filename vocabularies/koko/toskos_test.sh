#!/bin/sh

INFILES="koko-metadata.ttl koko-test.ttl"
OUTFILE=koko-skos_test.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="-l fi --set-modified --no-enrich-mappings --break-cycles --eliminate-redundancy --namespace=http://www.yso.fi/onto/koko/"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
