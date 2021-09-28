#!/bin/sh

INFILES="kulo-metadata.ttl kuloYso.rdf-xml-ONKIin.owl"
OUTFILE=kulo-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
