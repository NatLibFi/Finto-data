#!/bin/sh

INFILE="geo.ttl"
YSOFILE="../yso/ysoKehitys.rdf"

INFILES="geo-metadata.ttl $INFILE $YSOFILE"
OUTFILE=geo-skos.ttl

SKOSIFYHOME="../../../Skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYHOME/skosify/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
