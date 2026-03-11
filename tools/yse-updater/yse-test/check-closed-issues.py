#!/usr/bin/python3
# coding=utf-8
from rdflib import Graph, Namespace, URIRef
from github import Auth, Github
import sys, json, datetime

skos = Namespace("http://www.w3.org/2004/02/skos/core#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")

if len(sys.argv) < 2:
    print("Usage: %s GitHub-credentials-file" % sys.argv[0], file=sys.stderr)
    sys.exit()
else:
  print("Starting to check matching homepages between YSE and closed GitHub issues, please wait..\n")

yse_file = sys.argv[1]
yse_skos = Graph().parse(yse_file, format='turtle')

yse_triples = []
homepages_in_yse = 0
for triple in yse_skos.triples((None, foaf['homepage'], None)):
    homepages_in_yse += 1
    yse_triples.append(triple)

secrets = json.load(open(sys.argv[3]))
auth = Auth.Token(secrets['token'])
g = Github(auth=auth)
repo = g.get_user('NatLibFi').get_repo('YSE-test')
need_inspection = repo.get_issues(state='closed')

gh_issue_urls = []
for issue in need_inspection:
    gh_issue_urls.append(issue.html_url)

yse_triples_set = set(yse_triples)
gh_issue_urls_set = set([u.strip() for u in gh_issue_urls])

# Iterate over YSE resources with foaf:homepage and remove those whose homepage matches a closed issue URL
how_many_triples_to_remove = 0
for triple in yse_triples_set:
    homepage_str = str(triple[2]).strip()

    if homepage_str in gh_issue_urls_set:
        print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        print(f'> The suggestion with the uri {triple[0]} has been taken into YSE')
        print(f'> Matching foaf:homepage (GitHub issue URL) is: {homepage_str}')

        yse_skos.remove((URIRef(triple[0]), None, None))
        yse_skos.remove((None, None, URIRef(triple[0])))
        print(f'> "{homepage_str}" removed\n')
        how_many_triples_to_remove += 1

print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
print(f'Closed issues total: {len(gh_issue_urls_set)}')
print(f'foaf:homepage triples in YSE: {homepages_in_yse}')
print(f'Amount of suggestions to be removed: {how_many_triples_to_remove}')


yse_target_file = sys.argv[2]
yse_target_skos = Graph()
yse_target_skos += yse_skos

yse_target_skos.serialize(destination=yse_target_file, format='turtle')
