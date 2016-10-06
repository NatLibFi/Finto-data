#!/bin/sh

./gfdc-from-docs.py

INFILES="gfdc-metadata.ttl gfdc.ttl"
OUTFILE=gfdc-skos.ttl

./gfdc-to-skos.py classes.csv glossary.csv metadata.csv >gfdc.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS="--set-modified"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
