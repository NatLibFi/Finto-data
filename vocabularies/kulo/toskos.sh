#!/bin/sh

INFILES="kulo-metadata.ttl kuloYso.rdf-xml-ONKIin.owl"
OUTFILE=kulo-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
