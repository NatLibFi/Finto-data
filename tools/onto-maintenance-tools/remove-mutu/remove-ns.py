#!/usr/bin/env python

from rdflib import *
import sys

ns = sys.argv[1]
onto_path = sys.argv[2]
out_put_path = sys.argv[3]

# Loading the ontology
g = Graph()
g.parse(onto_path, format='n3')


i = 0

for s, p, o in list(g):
	flag = False

	# Checking if any of the parts of the triple belong to the namespace
	if s.startswith(ns):
		flag = True
	elif p.startswith(ns):
		flag = True
	elif not isinstance(o, Literal) and o.startswith(ns):
		flag = True

	if flag:
		g.remove((s, p, o))
		i += 1
		print("Removed triple <" + str(s) + "> <" + str(p) + "> <" + str(o))

print("Amount of removed triples: " + str(i))

# Saving the reduced ontology
g.serialize(out_put_path, format='turtle')


