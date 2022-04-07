#!/usr/bin/python3
# coding=utf-8
import urllib.request, urllib.parse, urllib.error, sys, pickle, rdflib, json
import requests, time, calendar, datetime, sys
from rdflib import Graph, Namespace,RDF ,XSD ,OWL , URIRef, plugin, Literal
from github import Github
from urllib.parse import urlencode

ysans = "http://www.yso.fi/onto/ysa/"
skosns = "http://www.w3.org/2004/02/skos/core#"
newtriples = Graph()
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
dct = Namespace('http://purl.org/dc/terms/')
isothes = Namespace('http://purl.org/iso25964/skos-thes#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
ysa = Namespace('http://www.yso.fi/onto/ysa/')

if len(sys.argv) < 3:
    print("Usage: %s GitHub-credentials-file Finto-data-path" % sys.argv[0], file=sys.stderr)
    sys.exit()

secrets = json.load(open(sys.argv[1]))
finto_data = sys.argv[2]
ysa_file = finto_data + '/vocabularies/ysa/ysa-skos.ttl'
yse_file = finto_data + '/vocabularies/yse/yse-skos.ttl'

gh = Github(secrets['username'], secrets['password'])
repo = gh.get_user('Finto-ehdotus').get_repo('YSE')
label = repo.get_label('uusi')
need_inspection = repo.get_issues(state='closed', labels=[label])
ysa_skos = Graph().parse(ysa_file, format='turtle')
yse_skos = Graph().parse(yse_file, format='turtle')

def delete_triples(uri):
    yse_skos.remove((URIRef(uri), None, None))
    yse_skos.remove((None, None, URIRef(uri)))

def replaced_by(uri, title):
    new_uri = lookup(title)
    if(new_uri != ''):
        yse_skos.remove((None, None, URIRef(uri)))
        yse_skos.add((URIRef(uri), dct.isReplacedBy, URIRef(new_uri)))
        yse_skos.add((URIRef(uri), OWL.deprecated, Literal('true',datatype=XSD.boolean)))

for issue in need_inspection:
    if ('**Termiehdotus Fintossa:**' in issue.body):
        md_href = issue.body.split("**Termiehdotus Fintossa:**")[1]
        if md_href:
            suggestion_uri = ysa + md_href.split('page/')[1].replace(')', '')
            ysalab = ysa_skos.preferredLabel(suggestion_uri, lang='fi')
            yselab = yse_skos.preferredLabel(suggestion_uri, lang='fi')
            if yselab != '' and ysalab == yselab: # the suggestion has been taken into YSA with the same prefLabel
                print("deleting: " + issue.title)
                delete_triples(suggestion_uri)
            else:
                print(('add replacedBy to:' + suggestion_uri))

yse_skos.serialize(destination=yse_file, format='turtle')
