#!/bin/sh

INFILES="koko-metadata.ttl koko_test-2019-03-18.ttl"
OUTFILE=koko-skos_test-2019-03-18.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-l fi --set-modified --no-enrich-mappings --break-cycles --eliminate-redundancy --namespace=http://www.yso.fi/onto/koko/"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
