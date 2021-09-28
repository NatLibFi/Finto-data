#!/bin/sh

INFILES="ptvl.ttl ptvl-uri-conversion.ttl ptvl-metadata.ttl"
OUTFILE=ptvl-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--set-modified"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
