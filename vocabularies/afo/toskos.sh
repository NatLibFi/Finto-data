#!/bin/sh

JENAHOME="$HOME/sw/apache-jena"
INFILES="afo-metadata.ttl afoKehitys.ttl afo-excluded.nt yso-afo.ttl"
OUTFILE=afo-skos.ttl

$JENAHOME/bin/arq --data=afoKehitys.ttl --query=filter-afo.sparql --results=NT >afo-excluded.nt

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
