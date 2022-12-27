#!/bin/sh

#Skosify installed with "sudo pip3 install --upgrade skosify"

INFILES="maotao.ttl maotao-metadata.ttl ysoKehitys-2022-1-Filolaos.ttl"
OUTFILE=maotao-skos.ttl

CONFFILE="finnonto.cfg"
LOGFILE=skosify.log

#skosify -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
~/ontology/SKOSIFY/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

