#!/bin/sh

INFILES="yse-metadata.ttl yse.ttl"
OUTFILE=yse-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-mark-top-concepts --no-enrich-mappings --no-aggregates"

python $SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
