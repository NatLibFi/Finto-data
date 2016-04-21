#!/usr/bin/env python

# Utility to generate dct:modified timestamps (xsd:date) for SKOS concepts.

# The idea is that for each concept, a hash (MD5) is calculated based on the
# triples where that concept is either the subject or object. Whenever the
# triples change, the hash will be different. A separate TSV data file of
# earlier hashes and timestamps is maintained.

# For new concepts, no modified timestamp is initially given. However, the
# next time the concept changes, a timestamp is added. The idea is that for
# newly encountered concepts, we cannot know whether the concept has already
# existed a long time or not.

# The timestamp to give can be passed on the command line as the last
# parameter. If not given, today's date will be used as the default.

# input is Turtle syntax on stdin
# output is Turtle syntax on stdout

from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
import sys
import datetime
import hashlib
import os.path

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DCT = Namespace('http://purl.org/dc/terms/')

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s <timestampfile> [date]" % sys.argv[0]
    sys.exit(1)

tsfile = sys.argv[1]
if len(sys.argv) > 2:
    timestamp = sys.argv[2]
else:
    timestamp = datetime.date.today().isoformat()

# load existing timestamps
old_timestamps = {}
if os.path.exists(tsfile):
    with open(tsfile, 'r') as f:
        for line in f:
            uri, hash, mtime = line.strip().split()
            old_timestamps[URIRef(uri)] = (hash, mtime)

# load SKOS file
g = Graph()
g.load(sys.stdin, format='turtle')

# calculate hashes and timestamps for concepts
def concept_hash(concept):
    cgraph = Graph()
    for triple in g.triples((concept, None, None)):
        cgraph.add(triple)
    for triple in g.triples((None, None, concept)):
        cgraph.add(triple)
    nt = cgraph.serialize(destination=None, format='nt')
    sorted_nt = ''.join(sorted(nt.splitlines(True)))
    md5 = hashlib.md5()
    md5.update(sorted_nt)
    return md5.hexdigest()

new_timestamps = {}
for concept in g.subjects(RDF.type, SKOS.Concept):
    hash = concept_hash(concept)

    if concept in old_timestamps:
        old_hash, old_mtime = old_timestamps[concept]
        if old_hash == hash:
            # hash is the same, maintain old timestamp
            new_timestamps[concept] = (old_hash, old_mtime)
            continue
        else:
            # hash has changed, update timestamp
            new_timestamps[concept] = (hash, timestamp)
    else:
        if len(old_timestamps) == 0:
            # we don't know anything about history, no timestamp
            new_timestamps[concept] = (hash, '-')
        else:
            # the concept is new, update timestamp
            new_timestamps[concept] = (hash, timestamp)

# store the new timestamps in the timestamp data file
with open(tsfile, 'w') as f:
    for concept, cdata in sorted(new_timestamps.items()):
        hash, mtime = cdata
        print >>f, "\t".join((concept, hash, mtime))

# Add the new timestamps to the graph

for concept, cdata in new_timestamps.items():
    hash, mtime = cdata
    if mtime != '-':
        g.add((concept, DCT.modified, Literal(mtime, datatype=XSD.date)))

g.serialize(destination=sys.stdout, format='turtle')
