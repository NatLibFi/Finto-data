#!/bin/sh

~/sw/jena-fuseki1-1.3.0/s-put http://localhost:3030/ds/data http://www.yso.fi/onto/ysa/ merged-places-skos.ttl
~/sw/jena-fuseki1-1.3.0/s-put http://localhost:3030/ds/data http://ldf.fi/pnr/ pnr-skos.ttl
~/sw/jena-fuseki1-1.3.0/s-post http://localhost:3030/ds/data http://ldf.fi/pnr/ pnr-coordinates.ttl
