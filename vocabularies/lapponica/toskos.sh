#!/bin/sh

./lapponica-to-skos.py sanasto.txt >lapponica.ttl
./add-se-labels.py lapponica-labels-se.csv >lapponica-labels-se.ttl
./add-yso-mappings.py lapponica-yso.csv >lapponica-yso.ttl

INFILES="lapponica-metadata.ttl lapponica-labels-se.ttl lapponica-yso.ttl lapponica.ttl"
OUTFILE=lapponica-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--set-modified --eliminate-redundancy --no-enrich-mappings"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
