#!/bin/sh

INFILES="kaunokki-metadata.ttl kaunokki.ttl"
OUTFILE=kaunokki-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:au:kaunokki: -c kaunokki.cfg"


$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
