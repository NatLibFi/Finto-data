#!/bin/sh

~/sw/apache-jena/bin/arq \
	--data=../../vocabularies/ysa/ysa-skos.ttl \
	--data=../../vocabularies/allars/allars-skos.ttl \
	--query=merge-places.rq -q \
	>merged-places-skos.ttl
