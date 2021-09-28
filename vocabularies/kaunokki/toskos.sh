#!/bin/sh

INFILES="kaunokki-metadata.ttl kaunokki.ttl"
OUTFILE=kaunokki-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:au:kaunokki: -c kaunokki.cfg"


$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
