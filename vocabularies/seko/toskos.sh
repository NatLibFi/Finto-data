#!/bin/sh

INFILES="seko-metadata.ttl seko-decoded.ttl"
OUTFILE=seko-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

/usr/local/virtualenvs/skosify/bin/python3 unidecode-hidden-labels.py seko.ttl>seko-decoded.ttl
$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
rm seko-decoded.ttl
