#!/bin/sh

#INFILES="hklj-metadata.ttl hklj.ttl"
INFILES="hklj-metadata.ttl hklj-tbc-validoitu.ttl"
OUTFILE=hklj-skos-20221205-valmis.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:hklj: --mark-top-concepts"


$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
