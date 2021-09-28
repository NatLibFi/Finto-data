#!/bin/sh

#Skosify installed with "sudo pip3 install --upgrade skosify"

INFILES="pto.ttl pto-metadata.ttl ysoKehitys-Cicero-2019.ttl"
OUTFILE=pto-skos.ttl

CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

#skosify -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
../../../Skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

