#!/bin/sh

INFILES="valo-metadata.ttl valo.ttl ../yso/ysoKehitys.rdf"
OUTFILE=valo-skos.ttl

SKOSIFYHOME="../../../Skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
