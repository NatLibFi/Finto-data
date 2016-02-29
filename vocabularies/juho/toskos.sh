#!/bin/sh

INFILE="juho.ttl"
YSOFILE="../yso/ysoKehitys.rdf"

INFILES="juho-metadata.ttl $INFILE $YSOFILE"
OUTFILE=juho-skos.ttl

SKOSIFYHOME="../../../Skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYHOME/skosify/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
