#!/bin/sh

INFILES="mesh-metadata.ttl mesh-sv-en.nt mesh-fi.ttl"

OUTFILE=mesh-skos.ttl
SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

echo 'Running skosify...'
$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

echo 'Done!'
