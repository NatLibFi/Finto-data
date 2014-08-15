#!/bin/sh

INFILES="sapo-generation.ttl sapo-skos-schema.ttl tisc.rdf"
OUTFILE=sapo-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--infer --no-mark-top-concepts --default-language fi"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
