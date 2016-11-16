#!/bin/sh

cp ../yso/ysoKehitys.rdf yso-import.rdf

INFILE="juho.ttl"
INFILES="juho-metadata.ttl yso-import.rdf $INFILE"
OUTFILE=juho-skos.ttl

SKOSIFYHOME="../../../Skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYHOME/skosify/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
