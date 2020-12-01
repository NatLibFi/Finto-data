#!/bin/sh

INFILES="hero.ttl"
#INFILES="hero-combined.ttl"
OUTFILE=hero-skos.ttl

LOGFILE=skosify.log
OPTS="--namespace http://www.yso.fi/onto/hero/ -c ../../conf/skosify/finnonto.cfg"

skosify $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
