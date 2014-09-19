#!/usr/bin/env python

import sys

# TODO: add the possibility that the script sniffs the baseURI from the ontology file itself

onto_path = sys.argv[1]
baseURI = sys.argv[2]

# baseURI declaration for TBC
print("# baseURI: " + baseURI + "\n\n")


f=open(onto_path,'r')

for line in f.readlines():
    print(line.rstrip("\n"))

f.close()
