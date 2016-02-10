#!/bin/sh

INFILES="jhsmeta.rdf"
OUTFILE=jhsmeta-skos.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
