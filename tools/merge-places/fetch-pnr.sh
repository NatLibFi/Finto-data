#!/bin/sh

#~/sw/jena-fuseki1-1.3.0/s-query --service=http://ldf.fi/pnr/sparql --query=pnr-to-skos.rq >pnr-skos.ttl
~/sw/jena-fuseki1-1.3.0/s-query --service=http://ldf.fi/pnr/sparql --query=pnr-coordinates.rq >pnr-coordinates.ttl
 