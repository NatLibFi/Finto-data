#!/bin/sh

INFILES="kto-metadata.ttl kto.rdf-xml-ONKIin.owl"
OUTFILE=kto-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
