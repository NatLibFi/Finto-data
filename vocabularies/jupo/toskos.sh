#!/bin/sh

INFILES="jupo-metadata.ttl jupo.ttl yso-jupo.ttl"
OUTFILE=jupo-skos.ttl

SKOSIFYHOME="../../tools/skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
