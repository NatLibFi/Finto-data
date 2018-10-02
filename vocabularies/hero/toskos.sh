#!/bin/sh

INFILES="hero-combined.ttl"
OUTFILE=hero-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://www.yso.fi/onto/hero/ -c ../../conf/skosify/finnonto.cfg"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
