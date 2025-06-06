import rdflib

from rdflib import Graph, URIRef
from rdflib.namespace import SKOS
import argparse

# Komentoparametrijäsennin
parser = argparse.ArgumentParser(description="Lists references in RDF model to deprecated resources")

# Parametri RDF-tiedostolle
parser.add_argument('turtleFile', type=str, help='The file containing the RDF model (in .ttl)')

# Parametri deprekoitujen URI:en listalle
parser.add_argument('deprecatedList', type=str, help='The file containing deprecated resources')

# Jäsennä parametrit
args = parser.parse_args()
modelFile = args.turtleFile
deprecatedList = args.deprecatedList


g = Graph()
g.parse(modelFile, format="turtle")

with open(deprecatedList, "r") as file:
    uris = [line.strip() for line in file]

# Käydään läpi jokainen URI ja etsitään kaikki skos:exactMatch-suhteet
matches = {}
for uri in uris:
    uri_ref = URIRef(uri.replace('<','').replace('>',''))
    # Etsitään kaikki subjektit, jotka ovat skos:exactMatch-suhteessa annettuun URI:iin
    for subject in g.subjects(SKOS.exactMatch, uri_ref):
        if uri not in matches:
            matches[uri] = []
        matches[uri].append(str(subject))

print("Nämä käsitteet on deprekoitu RDA registryssä:\n")
for uri, subjects in matches.items():
    for subject in subjects:
        print(subject)
