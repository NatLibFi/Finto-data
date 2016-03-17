#!/bin/sh

INFILES="koko-metadata.ttl koko.ttl"
OUTFILE=koko-skos.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS="-l fi --set-modified --no-enrich-mappings --break-cycles --eliminate-redundancy --namespace=http://www.yso.fi/onto/koko/"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
