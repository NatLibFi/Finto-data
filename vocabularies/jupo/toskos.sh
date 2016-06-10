#!/bin/sh

INFILES="jupo.ttl jupo-metadata.ttl yso-jupo.ttl"
OUTFILE=jupo-skos.ttl

SKOSIFYHOME="/home/terminologi/ontology/SKOSIFY/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

