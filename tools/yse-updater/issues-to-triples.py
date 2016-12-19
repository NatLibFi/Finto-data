#!/usr/bin/python
# coding=utf-8
import ghsecrets
import csv, urllib, sys, pickle, rdflib, json
import requests, time, calendar, datetime
from urllib import urlencode
from rdflib import Graph, Namespace,RDF ,XSD, URIRef, plugin, Literal
from github import Github

ysans = "http://www.yso.fi/onto/ysa/"
skosns = "http://www.w3.org/2004/02/skos/core#"
newtriples = Graph()
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
dct = Namespace('http://purl.org/dc/terms/')
isothes = Namespace('http://purl.org/iso25964/skos-thes#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
ysa = Namespace('http://www.yso.fi/onto/ysa/')
ysemeta = Namespace("http://www.yso.fi/onto/yse-meta/")
ysameta = Namespace("http://www.yso.fi/onto/ysa-meta/")

newtriples.bind('skos', skos)
newtriples.bind('dc', dct)
newtriples.bind('isothes', isothes)
newtriples.bind('foaf', foaf)
newtriples.bind('ysa', ysa)
newtriples.bind('ysa-meta', ysameta)

g = Github(ghsecrets.username, ghsecrets.password)
repo = g.get_user('Finto-ehdotus').get_repo('YSE')
newlab = repo.get_label('uusi')
accept_lab = repo.get_label('vastaanotettu')

timeframe = datetime.datetime.now() - datetime.timedelta(days=2)

new_issues = repo.get_issues(labels=[accept_lab], since=timeframe, state='open')

yse_skos = Graph().parse('yse-skos.ttl', format='turtle')

edit_issues = True
if len(sys.argv) > 1 and 'debug' in sys.argv:
    edit_issues = False

def headingToProperty(block):
    propHeading = block.split('\n', 1)[0].strip()
    headToProp = {
    'Ehdotettu termi suomeksi': 'prefLabel',
    'Ehdotettu termi ruotsiksi': 'prefLabel',
    'Ehdotettu termi englanniksi': 'prefLabel',
    'Ehdotetut temaattiset ryhmät (YSA-ryhmät)': 'member',
    'Ehdotettu yläkäsite YSOssa (LT)': 'broadMatch',
    'Tarkoitusta täsmentävä selite': 'note',
    'Vaihtoehtoiset termit ja ilmaisut': 'altLabel',
    'Alakäsitteet (RT)': 'narrowMatch',
    'Assosiatiiviset (ST)': 'relatedMatch',
    }
    if propHeading in headToProp:
        return headToProp[propHeading]
    return False

def guessLang(block):
    if 'ruotsiksi' in block:
        return 'sv'
    elif 'englanniksi' in block:
        return 'en'
    return 'fi'

def addPropertyValueTriples(prop, block, uri):
    vals = filter(None, block.split('\n')[1:])
    for value in vals:
        value = value.strip()
        if value == '': # skipping empty lines
            continue
        if prop == 'member':
            group_number = value[1:3]
            group_uri = 'http://www.yso.fi/onto/ysa/ryhma_' + group_number
            newtriples.add( (rdflib.term.URIRef(group_uri), skos.member, rdflib.term.URIRef(uri)) )
        elif '](http://' not in value:
            val_lang = guessLang(block)
            newtriples.add( (rdflib.term.URIRef(uri), rdflib.term.URIRef(skos + prop), rdflib.term.Literal(value, lang=val_lang)) )
        else:
            value_uri = value.split('(')[1][:-1]
            newtriples.add( (rdflib.term.URIRef(uri), rdflib.term.URIRef(skos + prop), rdflib.term.URIRef(value_uri)) )

def issueToTriple(issue):
    md_blocks = issue.body.split('#### ')
    uri = ysa + 'Y' + str(issue.number + 500000)
    if ('Käsitteen tyyppi   \n\nGEO \n\n'.decode('utf-8') in md_blocks):
        newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(ysameta + 'GeographicalConcept')) )
    newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(skos + 'Concept')) )
    newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(ysemeta + 'Concept')) )
    newtriples.add( (rdflib.term.URIRef(uri), foaf.homepage, rdflib.term.URIRef('https://github.com/Finto-ehdotus/YSE/issues/' + str(issue.number))) )
    newtriples.add( (rdflib.term.URIRef(uri), dct.created, rdflib.Literal(issue.created_at.date(), datatype=XSD.date)) )

    for block in md_blocks:
        if '**' in block:
            block = block.split('**')[0]
        prop = headingToProperty(block)
        # with skos:note the newlines rarely indicate a new property value
        # counting the newlines (a standard response has 4 or 5 newlines)
        if prop == 'note' and block.count('\n') > 5:
            heading = block.split('\n', 1)[0]
            # combining the multiline string into a single value by replacing newlines with spaces
            value = block.split('\n', 1)[1].replace('\n', ' ')
            block = heading + '\n' + value
        if (prop and len(block.split('\n', 1)) > 1):
            addPropertyValueTriples(prop, block, uri)

for issue in new_issues:
    uri = 'http://finto.fi/yse/fi/page/Y' + str(issue.number + 500000)
    if newlab not in issue.labels or issue.number < 4500: # early issues have been handled separately
        continue
    # skipping suggestions that have already been added to YSE
    if yse_skos.value(subject=rdflib.term.URIRef(uri), predicate=RDF.type):
        continue
    newbody = issue.body
    if 'Termiehdotus Fintossa' not in newbody:
        newbody = newbody + '**Termiehdotus Fintossa:** [' + issue.title + '](' + uri + ')'
    issueToTriple(issue)
    if edit_issues == True:
        issue.edit(body=newbody);
        issue.remove_from_labels(accept_lab)

def getYsaLabel(uri):
  if uri not in labels:
    params = urlencode({'uri': uri, 'format': 'application/json', 'lang': 'fi'})
    api = 'http://dev.finto.fi/rest/v1/ysa/label?'
    url = api + params
    try:
      response = requests.get(url).json()['prefLabel']
      labels[uri] = response
      return response
    except:
      return uri
  else:
    return labels[uri]

newtriples.serialize(destination='yse-new.ttl', format='turtle')
yse_skos.parse('yse-new.ttl', format='turtle')
yse_skos.serialize(destination='yse-skos.ttl', format='turtle')
