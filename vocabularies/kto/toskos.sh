#!/bin/sh

INFILES="kto-metadata.ttl kto.rdf-xml-ONKIin.owl"
OUTFILE=kto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
