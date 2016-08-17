#!/bin/sh

INFILES="seko-metadata.ttl seko-decoded.ttl"
OUTFILE=seko-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

./unidecode-hidden-labels.py seko.ttl>seko-decoded.ttl
$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
rm seko-decoded.ttl
