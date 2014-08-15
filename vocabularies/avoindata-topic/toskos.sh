#!/bin/sh

INFILES=avoindatafi_topic.rdf
OUTFILE=avoindata-topic-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
