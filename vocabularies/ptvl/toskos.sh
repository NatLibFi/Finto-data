#!/bin/sh

./ptvl-from-docs.py
./ptvl-to-skos.py

INFILES="ptvl.ttl ptvl-metadata.ttl"
OUTFILE=ptvl-skos.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS="--set-modified"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
