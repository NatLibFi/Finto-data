#!/bin/sh

INFILES="mesh-metadata.ttl mesh-skos.nt finmesh.ttl altlabels.ttl"

# mesh-skos.nt : tuotettu hdt:lla, ks ohjeet.txt
# finmesh.ttl : tuotettu Terkon sanalistasta, joka on muodossa prefLabel@en, prefLabel@fi, mahdolliset altLabel@fi
# altlabels.ttl : tuotettu KI:n synonyymilistasta CSV:stä RDF:ksi

OUTFILE=mesh-skos.ttl
SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log



echo 'Running skosify...'
$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

echo 'Done!'
