#!bin/python3 # Change this if needed
# coding=utf-8
import sys, rdflib
from rdflib import Namespace, URIRef, RDF

# dct = Namespace('http://purl.org/dc/terms/')
# foaf = Namespace('http://xmlns.com/foaf/0.1/')
# isothes = Namespace('http://purl.org/iso25964/skos-thes#')
# ns1 = Namespace('http://purl.org/termed/properties/')
owl = Namespace("http://www.w3.org/2002/07/owl#")
# rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# skos = Namespace("http://www.w3.org/2004/02/skos/core#")
# tero = Namespace("http://www.yso.fi/onto/tero/")
terometa = Namespace("http://www.yso.fi/onto/tero-meta/")
# xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
# ykl = Namespace("http://urn.fi/URN:NBN:fi:au:ykl:")
# ysa = Namespace('http://www.yso.fi/onto/ysa/')
# yso = Namespace("http://www.yso.fi/onto/yso/")


g = rdflib.Graph()
g.parse(open(sys.argv[1], "r"), format="turtle")

g.remove((None, URIRef("http://purl.org/termed/properties/id"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/createdBy"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/createdDate"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/graph"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/lastModifiedBy"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/lastModifiedDate"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/number"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/uri"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/code"), None))
g.remove((None, URIRef("http://purl.org/termed/properties/type"), None))

g.add((terometa.Concept, rdfs.subClassOf, owl.Class))
g.add((terometa.Class, rdfs.subClassOf, owl.Class))   

for s, p, o in g.triples((None, None, None)):
    if s.startswith("http://www.yso.fi/onto/tero"):
      print(f"Teroo {s}")
      g.add((s, RDF["type"], terometa.Concept))

file_to_be_saved = open(sys.argv[2], "w+")
file_to_be_saved.write(g.serialize(format="turtle").decode("utf-8"))
file_to_be_saved.close()

# Some instructions (if needed):
# python3 -m venv ./vocabularies
# cd vocabularies/
# ../bin/pip3 install rdflib
#./cleanAndFixTero.py source_file.ttl destination_file.ttl
