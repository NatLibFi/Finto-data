#!/bin/sh

INFILES="tero-metadata.ttl tero.ttl yso-tero.ttl"
OUTFILE=tero-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
#OPTS="-c tero.cfg -l fi -f turtle"
OPTS="-c ../../conf/skosify/finnonto.cfg -l fi -f turtle"

./add-tero-types.py $INFILES | $SKOSIFYHOME/skosify.py $OPTS - -o $OUTFILE 2>$LOGFILE
