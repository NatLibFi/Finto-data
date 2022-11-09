#!./../vocabularies/bin/python3
# coding=utf-8
import urllib.parse, sys, os, rdflib
from rdflib import Graph, Namespace, URIRef, RDF, Literal
#from rdflib.namespace import SKOS, XSD, DC
from rdflib.namespace import OWL, XSD, OWL, SKOS, RDFS

# owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
dct = Namespace('http://purl.org/dc/terms/')
dc = Namespace('http://purl.org/dc/elements/1.1/')
ns3 = Namespace('http://purl.org/termed/properties/')
skosext = Namespace('http://purl.org/finnonto/schema/skosext#')
yso = Namespace('http://www.yso.fi/onto/yso/')
ysometa1 = Namespace('http://www.yso.fi/onto/yso-meta/')
ysokehitys = Namespace('http://www.yso.fi/onto/yso-kehitys/')
ysometa = Namespace('http://www.yso.fi/onto/yso-meta/2007-03-02/')
juho = Namespace('http://www.yso.fi/onto/juho/')
juhometa = Namespace('http://www.yso.fi/onto/juho-meta/')

juho_graph = rdflib.Graph()
juho_graph.parse(open(sys.argv[1], "r"), format="turtle")
file_to_be_saved = open(sys.argv[2], "w+")

# **** JUHO-erikoisontologia ******
for s1, p1, o1 in juho_graph.triples((None, rdfs['subClassOf'], None)):
  if (URIRef(juho) in o1):
    for s2, p2, o2 in juho_graph.triples((o1, OWL.equivalentClass, None)):
      if (URIRef(yso) in o2): 
        juho_graph.add((s1, RDFS.subClassOf, o2))
        print(f'Käsitteelle {s1} lisättiin yläluokaksi (rdfs:subClassOf) {o2}')

for s, p, o in juho_graph.triples((None, None, None)):
  if (URIRef(juho) in s and OWL.equivalentClass in p and URIRef(yso) in o):
    juho_graph.add((s, rdf['type'], ysometa['DeprecatedConcept']))
    juho_graph.add((s, ysometa['deprecatedReplacedBy'], o))
    juho_graph.remove((s, rdf['type'], juhometa['Concept']))
    juho_graph.remove((s, OWL.equivalentClass, o))
    print(f'Käsitteeltä {s} poistettiin juhometa:Concept ja sille lisättiin tyypiksi ysometa:DeprecatedConcept')
    print(f'Käsitteelle {s} lisättiin poistuvan ekvivalenssin korvaava suhde ysometa:deprecatedReplacedBy {o}')
    
    # print(s + " a ysometa:DeprecatedConcept AND ysometa:deprecatedReplacedBy " + o)

# Poistetaan hasPoiminta

for s, p, o in juho_graph.triples((None, None, None)):
  if(juhometa['hasPoiminta'] in p):
    juho_graph.remove((s, juhometa['hasPoiminta'], o))
    print(f'Poistettiin {s}, juhometa:hasPoiminta, {o}')

file_to_be_saved.write(juho_graph.serialize(format="turtle"))

file_to_be_saved.close()

