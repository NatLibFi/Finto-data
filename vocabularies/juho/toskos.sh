#!/bin/sh

INFILE="juhoKehitys.ttl"
INFILES="juho-metadata.ttl -"
OUTFILE=juho-skos.ttl

MERGEHIER="../../tools/merge-hierarchy/merge-hierarchy.py"
SKOSIFYHOME="../../tools/skosify"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi -f turtle"

$MERGEHIER $INFILE | $SKOSIFYHOME/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
