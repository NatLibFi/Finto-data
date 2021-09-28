#!/bin/sh

INFILES="musa-metadata.ttl musa-merged.ttl"
OUTFILE=musa-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="-c ../../tools/oai-pmh-to-skos/skosify.cfg"

$SKOSIFYCMD $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
