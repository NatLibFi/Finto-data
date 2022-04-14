#!/usr/bin/python3
# coding=utf-8
from rdflib import Graph, Namespace, URIRef
from github import Github
import sys, json, datetime

skos = Namespace("http://www.w3.org/2004/02/skos/core#")

if len(sys.argv) < 3:
    print("Usage: %s GitHub-credentials-file Finto-data-path" % sys.argv[0], file=sys.stderr)
    sys.exit()
else:
  print("Starting to check matching labels between YSE and closed GitHub issues, please wait..\n")

yse_file = sys.argv[2] + '/vocabularies/yse/yse-skos.ttl'
# yse_file = sys.argv[2] + '/yse-skos.ttl' # only for testing purposes
yse_skos = Graph().parse(yse_file, format='turtle')

yse_triples = []
preflabels_in_yse = 0
for triple in yse_skos.triples((None, skos['prefLabel'], None)):
    preflabels_in_yse += 1
    yse_triples.append(triple)

secrets = json.load(open(sys.argv[1]))
gh = Github(secrets['username'], secrets['password'])
repo = gh.get_user('Finto-ehdotus').get_repo('YSE')
need_inspection = repo.get_issues(state='closed')

gh_titles = []
for issue in need_inspection:
    gh_titles.append(issue.title)

yse_triples_set = set(yse_triples)
gh_titles_stripped = [i.strip() for i in gh_titles]
gh_titles_set = set(gh_titles_stripped)

how_many_tripes_to_remove = 0
for triple in yse_triples_set:
    if triple[2].strip() in gh_titles_set:
      print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
      print(f'> The suggestion with the uri {triple[0]} has been taken into YSO\r')
      print(f'> Matching prefLabel or altLabel is: {triple[2]}\r')
      yse_skos.remove((URIRef(triple[0]), None, None))
      yse_skos.remove((None, None, URIRef(triple[0])))
      print(f'> "{triple[2]}" removed\n')
      how_many_tripes_to_remove += 1

print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
print(f'Closed issues total: {len(gh_titles_set)}')
print(f'prefLabels in YSE: {preflabels_in_yse}')
print(f'Amount of suggestions to be removed: {how_many_tripes_to_remove}')

yse_skos.serialize(destination=yse_file, format='turtle')

