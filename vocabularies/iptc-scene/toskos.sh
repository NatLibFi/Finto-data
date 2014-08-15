#!/bin/sh

INFILES="iptc-scene-metadata.ttl cptall-en-GB.rdf"
OUTFILE=iptc-scene-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
