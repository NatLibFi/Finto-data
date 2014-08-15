#!/bin/sh

SKOSIFY=../skosify/skosify.py
OPTS="--config skosify.cfg"

$SKOSIFY $OPTS ysa.rdf ../../vocabularies/ysa/ysa-metadata.ttl -o ysa.ttl 2>ysa-skosify.log
$SKOSIFY $OPTS allars.rdf ../../vocabularies/allars/allars-metadata.ttl -o allars.ttl 2>allars-skosify.log
$SKOSIFY $OPTS musa.rdf -o musa.ttl ../../vocabularies/musa/musa-metadata.ttl 2>musa-skosify.log
