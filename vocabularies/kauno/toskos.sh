#!/bin/sh

INFILE="kauno.ttl"
INFILES="kauno-metadata.ttl ../yso/releases/2023.6.Hypatia/ysoKehitys.rdf $INFILE"
OUTFILE=kauno-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
