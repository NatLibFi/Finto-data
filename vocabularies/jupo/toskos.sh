#!/bin/sh

INFILES="jupo.ttl jupo-metadata.ttl ysoKehitys-2021-Epikuros.ttl"
OUTFILE=jupo-skos.ttl

SKOSIFYHOME="/home/terminologi/ontology/SKOSIFY/Skosify-master"
CONFFILE="/home/terminologi/ontology/SKOSIFY/finnonto.cfg"
LOGFILE=skosify.log

~/ontology/SKOSIFY/Skosify-master/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

