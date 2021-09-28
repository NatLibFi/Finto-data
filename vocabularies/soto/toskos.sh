#!/bin/sh

#INFILES="puho-metadata.ttl puho.ttl yso-puho.ttl"
INFILES="soto-metadata.ttl soto.ttl yso-soto.ttl"
OUTFILE=soto-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
