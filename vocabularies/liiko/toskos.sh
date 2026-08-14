#!/bin/sh

INFILES="mero.ttl mero-metadata.ttl ysoKehitysTBC_2026-3_Maimonides.ttl"
OUTFILE=mero-skos.ttl

CONFFILE=finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
~/ontology/python3venv/bin/python3 ~/ontology/SKOSIFY/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

