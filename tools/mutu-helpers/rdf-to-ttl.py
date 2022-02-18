#!/usr/bin/python3
#my_activated_python_env/bin/python3
# coding=utf-8
# You may need to install rdflib. If so, run pip install rdflib. 
# If you are working in a Python virtual environment:
# run pip3 install rdflib
# Run the script this way:
# ./rdf-to-ttl.py [source-folder]/file.rdf [target-folder]/file.ttl

import sys, rdflib

g = rdflib.Graph()
g_target = rdflib.Graph()
g.parse(open(sys.argv[1], "r"), format="xml")
file_to_be_saved = open(sys.argv[2], "w+")

for s, p, o in g.triples((None, None, None)):
    g_target.add((s, p, o))

print("Amount of triples in the original")
print(len(g))
print("Amount of triples in the target")
print(len(g_target))

file_to_be_saved.write(g_target.serialize(format="turtle"))
file_to_be_saved.close()

