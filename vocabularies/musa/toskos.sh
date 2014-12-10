#!/bin/sh

INFILES="musa-metadata.ttl musa-merged.ttl"
OUTFILE=musa-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c ../../tools/oai-pmh-to-skos/skosify.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
