#!/bin/sh

cp ../yso/ysoKehitys.rdf yso-import.rdf

INFILE="juho.ttl"
INFILES="juho-metadata.ttl yso-import.rdf juho-en-sv.ttl juho-singular.ttl $INFILE"
OUTFILE=juho-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYHOME/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
