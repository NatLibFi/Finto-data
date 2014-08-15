#!/bin/sh

INFILES="lapponica-metadata.ttl lapponica.ttl"
OUTFILE=lapponica-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
