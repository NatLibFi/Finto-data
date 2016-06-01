#!/bin/sh

INFILES="maotao-metadata.ttl maotao.ttl yso-maotao.ttl"
OUTFILE=maotao-skos.ttl

SKOSIFYHOME="../../../Skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
