#!/bin/sh

INFILE="kauno.ttl"
INFILES="kauno-metadata.ttl ../yso/releases/2025.7.Laotse/ysoKehitys.rdf $INFILE"
OUTFILE=kauno-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
