#!/bin/sh

INFILES="koko-metadata.ttl koko.ttl"
OUTFILE=koko-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-l fi --break-cycles --eliminate-redundancy --namespace=http://www.yso.fi/onto/koko/"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
