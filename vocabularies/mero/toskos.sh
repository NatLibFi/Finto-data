#!/bin/sh

INFILES="mero-metadata.ttl merisanastox110309.rdf-xml-ONKIin.owl"
OUTFILE=mero-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
