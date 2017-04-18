#!/bin/sh

# Convert YSO to MARC
./yso-to-marc.py ../../vocabularies/yso/yso-skos.ttl >yso.mrcx

# Fix XML attribute order so that Aleph understands it, and reformat to more human-readable XML
catmandu convert MARC --type XML to MARC --type XML <yso.mrcx | xmllint --format - >yso-formatted.mrcx
