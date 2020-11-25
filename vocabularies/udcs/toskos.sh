#!/bin/sh

INFILES="udcs-metadata.ttl udc-scheme.rdf udk-skos.ttl"
OUTFILE=udcs-skos.ttl

SKOSIFYHOME="../../../Skosify"
LOGFILE=skosify.log
OPTS="--namespace http://udcdata.info/ -c udcs.cfg"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
