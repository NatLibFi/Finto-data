#!/bin/sh

YSOFILE="../yso/ysoKehitys.rdf"
INFILES="mero-metadata.ttl mero.ttl $YSOFILE"
OUTFILE=mero-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
