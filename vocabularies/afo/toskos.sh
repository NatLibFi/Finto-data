#!/bin/sh

INFILE="afoKehitys.ttl"
FILTEREDFILE="afo-filtered.ttl"
INFILES="afo-metadata.ttl yso-afo.ttl $FILTEREDFILE"
OUTFILE=afo-skos.ttl

JENAHOME="$HOME/sw/apache-jena"

$JENAHOME/bin/arq --data=$INFILE --query=filter-afo.sparql >$FILTEREDFILE

SKOSIFYHOME="../../../Skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
