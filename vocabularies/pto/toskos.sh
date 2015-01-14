#!/bin/sh

INFILES="pto-metadata.ttl paikkatieto-ei45-eiinspire-puritettu.ttl"
OUTFILE=pto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c pto2skos.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
