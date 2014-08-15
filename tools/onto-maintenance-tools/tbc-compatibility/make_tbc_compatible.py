#!/usr/bin/env python

import sys

onto_path = sys.argv[1]
baseURI = sys.argv[2]

# baseURI declaration for TBC
print("# baseURI: " + baseURI + "\n\n")

f=open(onto_path,'r')

for line in f.readlines():
    print(line.rstrip("\n"))

f.close()
