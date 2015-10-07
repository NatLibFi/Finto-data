#!/bin/sh

INFILES="udcs-metadata.ttl udc-scheme.rdf udcsummary-skos.rdf"
OUTFILE=udcs-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://udcdata.info/ -c udcs.cfg"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
