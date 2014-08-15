#!/bin/sh

INFILES="puho-metadata.ttl yso-puho.rdf-xml-ONKIin.owl"
OUTFILE=puho-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
