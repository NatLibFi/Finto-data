#!/bin/sh

cp ../yso/ysoKehitys.rdf yso-import.rdf
INFILES="muso-metadata.ttl muso.ttl yso-import.rdf"
OUTFILE=muso-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
