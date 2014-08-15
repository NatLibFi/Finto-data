#!/bin/sh

INFILES="kito-metadata.ttl kito.rdf-xml-ONKIin.owl"
OUTFILE=kito-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
