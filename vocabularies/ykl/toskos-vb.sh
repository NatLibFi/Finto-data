#!/bin/bash

# YKL:n VocBenchin testiversion julkaisukomennot

SKOSIFYCMD="skosify"

INFILES="ykl-metadata.ttl ykl-vb.rdf ykl-hklj.ttl"
OUTFILE="ykl-vb-skos.ttl"
LOGFILE="skosify-vb.log"
OPTS="-c ykl-vb.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --mark-top-concepts -F turtle"

$SKOSIFYCMD $OPTS $INFILES >$OUTFILE 2>$LOGFILE
