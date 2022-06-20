#!/bin/sh

#INFILES="mehi-purified-ready-2022-05-05-a.ttl ../yso/releases/2021.3.Epikuros/ysoKehitys.rdf"
#INFILES="mehi-purified-ready-2022-06-03-a.ttl ../yso/releases/2021.3.Epikuros/ysoKehitys.rdf"
INFILES="mehi-purified-validated-fixed-and-ready-for-skosify-2022-06-20-a.ttl ../yso/releases/2021.3.Epikuros/ysoKehitys.rdf"
OUTFILE=oma-skos-2022-06-20-a.ttl

SKOSIFYCMD="skosify"
CONFFILE=./finnonto.cfg
LOGFILE=skosify.log

$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

