#!/bin/sh

INFILES="kauno-metadata.ttl kauno.owl"
OUTFILE=kauno-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
