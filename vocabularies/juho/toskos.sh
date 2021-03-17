#!/bin/sh

INFILE="juho.ttl"
INFILES="juho-metadata.ttl juho-singular.ttl juhoDeprecated.ttl recoveredDeletedConcepts.ttl ../yso/releases/2020.1.Diotima/ysoKehitys.rdf $INFILE"
OUTFILE=juho-skos.ttl

SKOSIFYCMD=skosify
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYCMD $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
