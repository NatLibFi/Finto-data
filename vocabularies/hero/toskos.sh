#!/bin/sh

INFILES="hero-metadata.ttl hero-combined.ttl"
OUTFILE=hero-skos.ttl

SKOSIFYHOME="../../../Skosify"
LOGFILE=skosify.log
OPTS="--namespace http://www.yso.fi/onto/hero/ -c ../../conf/skosify/finnonto.cfg"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
