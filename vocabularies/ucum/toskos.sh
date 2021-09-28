#!/bin/sh

INFILES="ucum-metadata.ttl ucum.ttl"
OUTFILE=ucum-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:ucum: --mark-top-concepts"
#-c udcs.cfg

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
