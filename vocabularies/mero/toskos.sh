#!/bin/sh

INFILES="mero-metadata.ttl mero.ttl"
OUTFILE=mero-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
