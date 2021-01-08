#!/bin/sh

INFILES="tero-metadata.ttl tero-yso-replacedby.ttl tero.ttl yso-tero.ttl"
OUTFILE=tero-skos.ttl

LOGFILE=skosify.log
#OPTS="-c tero.cfg -l fi -f turtle"
OPTS="-c ../../conf/skosify/finnonto.cfg -l fi -f turtle"

./add-tero-types.py $INFILES | skosify $OPTS - -o $OUTFILE 2>$LOGFILE
