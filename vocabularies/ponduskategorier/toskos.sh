#!/bin/sh

SKOSIFY="/home/oisuomin/svn/skosify"

$SKOSIFY/skosify.py -c $SKOSIFY/owl2skos.cfg ponduskategorier.rdf -l sv --label Ponduskategorier -o ponduskategorier-skos.ttl


