#!/bin/sh

#Skosify installed with "sudo pip3 install --upgrade skosify"

INFILES="maotao.ttl maotao-metadata.ttl ysoKehitys-Cicero-2019.ttl"
OUTFILE=maotao-skos.ttl

CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

skosify -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
#~/ontology/SKOSIFY/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

