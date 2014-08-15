#!/bin/sh

INFILES="juho-metadata.ttl juhoKehitys.ttl"
OUTFILE=juho-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYHOME/skosify.py $OPTS -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
