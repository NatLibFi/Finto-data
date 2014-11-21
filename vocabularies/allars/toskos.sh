#!/bin/sh

INFILES="allars-metadata.ttl allars-groups.ttl allars-linked.ttl"
OUTFILE=allars-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c ../../tools/oai-pmh-to-skos/skosify.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
