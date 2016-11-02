#!/bin/sh

INFILES="tsr-metadata.ttl tsr.ttl ../yso/ysoKehitys.rdf"
OUTFILE=tsr-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
