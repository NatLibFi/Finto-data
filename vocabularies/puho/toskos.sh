#!/bin/sh

INFILES="puho-metadata.ttl puho.ttl yso-puho.ttl"
OUTFILE=puho-skos.ttl

SKOSIFYHOME="../../../Skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
