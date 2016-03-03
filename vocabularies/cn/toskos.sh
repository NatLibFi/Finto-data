#!/bin/sh

INFILES="cn-metadata.ttl rdaa.ttl rdac.ttl cn.ttl"
OUTFILE=cn-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-mark-top-concepts --namespace http://urn.fi/URN:NBN:fi:au:cn:"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
