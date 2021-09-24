#!/usr/bin/python3
# coding=utf-8
# You may need to install rdflib. If so, run pip install rdflib. 
# If you are working in a Python virtual environment, run pip3 install rdflib
import sys, rdflib
from rdflib import Namespace

skos = Namespace("http://www.w3.org/2004/02/skos/core#")
kauno = Namespace('http://www.yso.fi/onto/kauno/')
kaunometa = Namespace('http://www.yso.fi/onto/kauno-meta/')

g = rdflib.Graph()
g.parse(open(sys.argv[1], "r"), format="turtle")
file_to_be_saved = open(sys.argv[2], "w+")

how_many_sections = 10

list_of_skos_members = []
count_members = 0
print("Collecting all the skos:members")
for sec_num in range(how_many_sections):
  print(f'section_{sec_num}')
  for s, p, o in g.triples((kaunometa[f'section_{sec_num}'], skos["member"], None)):
    list_of_skos_members.append(o)
    count_members += 1

print("All the skos:members collected:")
print(count_members)
 
# ---

list_of_skos_concepts_with_facet = []
count_concepts = 0
print("Collecting all the concepts containing facet information")
for sec_num in range(how_many_sections):
  for s, p, o in g.triples((None, kaunometa["facet"], kaunometa[f'section_{sec_num}'])):
    if s not in list_of_skos_members:
      g.add((o, skos["member"], s))
      print(f'Added a new triple {o} skos:member {s}')
      count_concepts += 1

print("Amount of the added concepts:")
print(count_concepts)

file_to_be_saved.write(g.serialize(format="turtle"))
file_to_be_saved.close()

