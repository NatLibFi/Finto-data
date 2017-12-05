#!/bin/sh

INFILES="tts-metadata.ttl tieto.ttl"
OUTFILE=tieto-skos.ttl

SKOSIFYHOME="../../../Skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:tts: -c tts.cfg"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
