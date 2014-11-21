#!/bin/sh

INFILES="ysa-linked.ttl ysa-metadata.ttl ysa-groups.ttl"
OUTFILE=ysa-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c ../../tools/oai-pmh-to-skos/skosify.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
