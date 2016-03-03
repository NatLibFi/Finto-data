#!/bin/sh

INFILES="cn-metadata.ttl rdaa.ttl rdac.ttl cn.ttl"
OUTFILE=cn-skos.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
CNLOGFILE=cn.log
OPTS="--no-mark-top-concepts --namespace http://urn.fi/URN:NBN:fi:au:cn:"

./convert-cn-to-skos.py >cn.ttl 2>$CNLOGFILE
$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
