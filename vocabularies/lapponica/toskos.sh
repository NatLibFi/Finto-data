#!/bin/sh

./add-se-labels.py lapponica-labels-se.csv >lapponica-labels-se.ttl

INFILES="lapponica-metadata.ttl lapponica-labels-se.ttl lapponica.ttl"
OUTFILE=lapponica-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
