#!/bin/sh

#INFILES="puho-metadata.ttl puho.ttl yso-puho.ttl"
INFILES="soto-metadata.ttl soto.ttl yso-soto.ttl"
OUTFILE=soto-skos.ttl

SKOSIFYHOME="../../../Skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
