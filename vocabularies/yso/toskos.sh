#!/bin/sh

INFILE=ysoKehitys.rdf
TTLFILE=ysoKehitys.ttl
OUTFILE=yso-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
TAGLOGFILE=removed-recent.log
LOGFILE=skosify.log

./tag-recently-added.py $INFILE >$TTLFILE 2>$TAGLOGFILE
$SKOSIFYHOME/skosify.py -c $CONFFILE $TTLFILE -o $OUTFILE 2>$LOGFILE
