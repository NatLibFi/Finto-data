#!/bin/sh

INFILES="genre.ttl"
OUTFILE=genre-skos.ttl

SKOSIFYHOME="../../../Skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:mts: -c ./genresanasto.cfg"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
