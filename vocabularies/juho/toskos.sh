#!/bin/sh

INFILES="juho-metadata.ttl juho-singular.ttl juho.ttl ../yso/releases/2025.7.Laotse/ysoKehitys.rdf"
OUTFILE=juho-skos.ttl

SKOSIFYCMD=skosify
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYCMD $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
