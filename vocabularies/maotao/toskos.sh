#!/bin/sh

INFILES="maotao.ttl maotao-metadata.ttl yso-maotao.ttl"
OUTFILE=maotao-skos.ttl

SKOSIFYHOME="/home/terminologi/ontology/SKOSIFY/"
CONFFILE=finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

