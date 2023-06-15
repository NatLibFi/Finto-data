#!/bin/sh

#INFILES="hklj-metadata.ttl hklj.ttl"
INFILES="hklj-metadata.ttl hklj.ttl"
OUTFILE=hklj-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:hklj: --mark-top-concepts"


$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
