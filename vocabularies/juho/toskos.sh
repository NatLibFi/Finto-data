#!/bin/sh

INFILE="~/codes/RDFTools/juho-uusi-yritys-2022-10-21/juho-skripti-ajettu-1-puritettu-plus-manuaaliset.ttl"
INFILES="juho-metadata.ttl juho-singular.ttl ../yso/releases/2020.1.Diotima/ysoKehitys.rdf $INFILE"
OUTFILE=juho-skos.ttl

SKOSIFYCMD=skosify
CONFFILE=../../conf/skosify/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi"

$SKOSIFYCMD $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
