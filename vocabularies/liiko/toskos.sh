#!/bin/sh

INFILES="mero.ttl mero-metadata.ttl ysoKehitys-2022-Filolaos.ttl"
OUTFILE=mero-skos.ttl

SKOSIFYHOME="/home/terminologi/ontology/SKOSIFY"
CONFFILE=finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYHOME/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

