#!/bin/sh

INFILES="lajisto-metadata.ttl FINTO_Mammalia.ttl"
OUTFILE=lajisto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c lajisto.cfg --namespace http://tun.fi/"


$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
