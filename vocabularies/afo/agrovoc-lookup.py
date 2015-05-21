#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef
import requests
import sys

# Namespace declarations
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
AFO = Namespace("http://www.yso.fi/onto/afo/")
AFOMETA = Namespace("http://www.yso.fi/onto/afo-meta/")
AGROVOC = Namespace("http://aims.fao.org/aos/agrovoc/")

# AGROVOC Skosmos REST API
#RESTBASE = 'http://aims.fao.org/skosmos/rest/v1/'

RESTBASE = "http://skosmos.dev.finto.fi/rest/v1/"

# read AFO
g = Graph()
g.parse(sys.argv[1], format='turtle')

# create output graph
out = Graph()
out.namespace_manager.bind('skos', SKOS)
out.namespace_manager.bind('afo', AFO)
out.namespace_manager.bind('agrovoc', AGROVOC)

# find agcx field values and look them up in AGROVOC using REST API
for conc, agcx in g.subject_objects(AFOMETA.agcx):
    params = { 'lang': 'en', 'label': agcx.strip() }
    req = requests.get(RESTBASE + 'agrovoc/lookup', params=params)
    if req.status_code == requests.codes.ok:
        data = req.json()
        results = data['results']
        if len(results) > 1:
            print >>sys.stderr, ("Warning: multiple results for <%s> '%s':" % (conc, agcx)), results
        for result in results:
            # add closeMatch relationships
            out.add((conc, SKOS.closeMatch, URIRef(result['uri'])))
    else:
        print >>sys.stderr, "Warning: no results for <%s> '%s'" % (conc, agcx)

out.serialize(destination=sys.stdout, format='turtle')
