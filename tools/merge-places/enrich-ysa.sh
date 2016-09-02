#!/bin/bash

time http_proxy=127.0.0.1:8123 ~/sw/pypy-env/bin/python enrich-ysa.py ~/git/Finto-data/vocabularies/ysa/ysa-skos.ttl mapping-results.ttl >ysa-enriched.ttl 2>log
