#!/bin/sh
cp ../yso/ysoKehitys.rdf yso-import.rdf
INFILES="valo-metadata.ttl valo.ttl yso-import.rdf"
OUTFILE=valo-skos.ttl

SKOSIFYHOME="../../../Skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
