#!/bin/sh

INFILES="oiko.ttl oiko-metadata.ttl ysoKehitys-01122016.ttl"
OUTFILE=oiko-skos.ttl

#SKOSIFYHOME="/home/terminologi/ontology/SKOSIFY/"
SKOSIFYHOME="../../tools/"
CONFFILE=finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

