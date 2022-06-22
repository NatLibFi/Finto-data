#!/bin/sh

INFILES="mehi.ttl ../yso/releases/2021.3.Epikuros/ysoKehitys.rdf"
OUTFILE=oma-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

