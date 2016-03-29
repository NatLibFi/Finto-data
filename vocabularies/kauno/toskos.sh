#!/bin/sh


INFILES="kauno-metadata.ttl kauno.ttl yso-kauno.ttl"
OUTFILE=kauno-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
