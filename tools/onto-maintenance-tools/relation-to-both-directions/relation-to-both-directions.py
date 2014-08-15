#!/usr/bin/env python

from rdflib import *
import os
import time
import sys


def add_another_direction(property, graph):

	for s, p, o in list(g):
		
		if p == property:
			print(s + " " + p + " " + o)
			triple = (o, p, s)
			
			# add the property to the other direction
			graph.add(triple)
			print("Added: " + str(triple))

            

property_uri = sys.argv[1]
onto_path = sys.argv[2]
out_put_path = sys.argv[3]

print(property_uri)

print(time.strftime("%H:%M:%S"))

g = Graph()
g.parse(onto_path, format='n3')


print(time.strftime("%H:%M:%S"))
add_another_direction(URIRef(property_uri), g)

print(time.strftime("%H:%M:%S"))

g.serialize(out_put_path, format='turtle')


print(time.strftime("%H:%M:%S"))

