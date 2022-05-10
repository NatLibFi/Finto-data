#!/bin/sh

INFILES="aika.ttl aika-meta.ttl"
OUTFILE=aika-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="-c aika.cfg"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
