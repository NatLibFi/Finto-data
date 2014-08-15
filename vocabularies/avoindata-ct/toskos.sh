#!/bin/sh

INFILES=avoindatafi_contentType.rdf
OUTFILE=avoindata-ct-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
