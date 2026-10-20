#!/usr/bin/python3
# coding=utf-8
import csv, urllib.request, urllib.parse, urllib.error, sys, pickle, rdflib, json
import requests, time, calendar, datetime
from urllib.parse import urlencode
from rdflib import Graph, Namespace,RDF ,XSD, URIRef, plugin, Literal
from github import Auth, Github

ysons = "http://www.yso.fi/onto/yso/"
skosns = "http://www.w3.org/2004/02/skos/core#"
newtriples = Graph()
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
dct = Namespace('http://purl.org/dc/terms/')
isothes = Namespace('http://purl.org/iso25964/skos-thes#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
yso = Namespace('http://www.yso.fi/onto/yso/')
yse = Namespace('http://www.yso.fi/onto/yse/')
ysemeta = Namespace("http://www.yso.fi/onto/yse-meta/")

newtriples.bind('skos', skos)
newtriples.bind('isothes', isothes)
newtriples.bind('foaf', foaf)
newtriples.bind('yso', yso)
newtriples.bind('yse', yse)
newtriples.bind('yse-meta', ysemeta)

if len(sys.argv) < 2:
    print("Usage: %s GitHub-credentials-file" % sys.argv[0], file=sys.stderr)
    sys.exit()

edit_issues = True
secrets = None
for arg in sys.argv:
    if arg == 'debug':
        edit_issues = False
    elif 'issues-to-triples' not in arg:
        with open(arg) as json_file:
          secrets = json.load(json_file)

auth = Auth.Token(secrets['token'])
g = Github(auth=auth)
repo = g.get_user('Finto-ehdotus').get_repo('YSE')
newlab = repo.get_label('uusi')
accept_lab = repo.get_label('vastaanotettu')

timeframe = datetime.datetime.now() - datetime.timedelta(days=90)

new_issues = repo.get_issues(labels=[accept_lab], since=timeframe, state='open')

yse_skos = Graph().parse('yse-skos.ttl', format='turtle')

# converts github-issue heading elements to skos-properties
def headingToProperty(block):
    propHeading = block.split('\n', 1)[0].strip()
    headToProp = {
    'Käsitteen tyyppi': 'type',
    'Ehdotettu termi suomeksi': 'prefLabel@fi',
    'Ehdotettu termi ruotsiksi': 'prefLabel@sv',
    'Ehdotettu termi englanniksi': 'prefLabel@en',
    'Ehdotetut temaattiset ryhmät': 'member',
    'Ehdotettu yläkäsite YSOssa (LT)': 'broadMatch',
    'Tarkoitusta täsmentävä selite': 'note',
    'Vaihtoehtoiset termit': 'altLabel',
    'Alakäsitteet (RT)': 'narrowMatch',  # typo, but in use
    'Alakäsitteet (ST)': 'narrowMatch',
    'Assosiatiiviset (RT)': 'relatedMatch',
    }
    if propHeading in headToProp:
        return headToProp[propHeading]
    return None

# creates new triples from the given block and adds them to the newtriples graph
def addPropertyValueTriples(prop, value, uri):
    if prop == 'type':
        if value == 'GEO':
            newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(ysemeta + 'GeographicalConcept')) )
    elif prop == 'member':
        group_number = value[1:3]
        group_uri = 'http://www.yso.fi/onto/yse/ryhma_' + group_number
        newtriples.add( (rdflib.term.URIRef(group_uri), skos.member, rdflib.term.URIRef(uri)) )
    elif '](http://' not in value:
        if '@' in prop:
            prop, val_lang = prop.split('@')
        else:
            val_lang = 'fi'
        newtriples.add( (rdflib.term.URIRef(uri), rdflib.term.URIRef(skos + prop), rdflib.term.Literal(value, lang=val_lang)) )
    else:
        for val in value.split(', '):
            value_uri = val.split('(')[1][:-1]
            newtriples.add( (rdflib.term.URIRef(uri), rdflib.term.URIRef(skos + prop), rdflib.term.URIRef(value_uri)) )

def parse_issue_body(body):
    cur_heading = None
    cur_value = []
    for line in body.splitlines():
        line = line.strip()
        if line == "":
            continue
        if line.startswith('**'):
            if cur_heading and cur_value:
                yield (cur_heading, ' '.join(cur_value))
            _, cur_heading, _ = line.split('**', maxsplit=2)
            cur_value = []
        else:
            cur_value.append(line)
    # return last one as well
    if cur_heading and cur_value:
        yield (cur_heading, ' '.join(cur_value))

# converts the github-issue markdown into skos triples
def issueToTriple(issue):
    uri = yso + 'Y' + str(issue.number + 500000)
    newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(skos + 'Concept')) )
    newtriples.add( (rdflib.term.URIRef(uri), RDF.type, rdflib.term.URIRef(ysemeta + 'Concept')) )
    newtriples.add( (rdflib.term.URIRef(uri), foaf.homepage, rdflib.term.URIRef('https://github.com/Finto-ehdotus/YSE/issues/' + str(issue.number))) )
    newtriples.add( (rdflib.term.URIRef(uri), dct.created, rdflib.Literal(issue.created_at.date(), datatype=XSD.date)) )

    for heading, value in parse_issue_body(issue.body):
        prop = headingToProperty(heading)
        if prop:
            addPropertyValueTriples(prop, value, uri)

# iterating through the new issues that have been marked with the "vastaanotettu" label
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

# looks up prefLabels for YSE uris from the finto api
def getYseLabel(uri):
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
yse_skos.serialize(destination='yse-skos-new.ttl', format='turtle')
