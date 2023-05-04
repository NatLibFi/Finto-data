#!/usr/bin/env python3

# Utility to generate dct:created and dct:modified timestamps (xsd:date) for
# SKOS concepts.

# The idea is that for each concept, a hash (MD5) is calculated based on the
# triples where that concept is either the subject or object. Whenever the
# triples change, the hash will be different. A separate TSV data file of
# earlier hashes and timestamps is maintained.

# First run
# If the tool is run with an empty or nonexistent timestamp file, no
# timestamps are added but hashes are stored in the timestamp file for later
# reference. The idea is that without preexisting timestamp information, we
# cannot know anything about how long the concepts have existed and when
# they were last modified. However, the next time a concept changes, the
# hash will be different and thus a modified timestamp is added and
# thereafter maintained whenever the concept changes.

# When a timestamp file exists and a new concept is encountered, it will be
# given a modified timestamp. It will also be given a created timestamp,
# unless it already has one in the data. Existing created timestamps will
# not be touched.

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
    print("Usage: %s <timestampfile> [date]" % sys.argv[0], file=sys.stderr)
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
            tsdata = line.strip().split()
            if len(tsdata) > 3:
                # new style timestamp file, both mtime and ctime
                uri, hash, mtime, ctime = tsdata
            else:
                # old style timestamp file, only mtime
                uri, hash, mtime = tsdata
                ctime = '-'
            old_timestamps[URIRef(uri)] = (hash, mtime, ctime)

# load SKOS file
g = Graph()
g.parse(sys.stdin, format='turtle')

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
    md5.update(sorted_nt.encode('utf-8'))
    return md5.hexdigest()

new_timestamps = {}
for concept in g.subjects(RDF.type, SKOS.Concept):
    hash = concept_hash(concept)

    if concept in old_timestamps:
        old_hash, old_mtime, old_ctime = old_timestamps[concept]
        if old_hash == hash:
            # hash is the same, maintain old timestamp
            new_timestamps[concept] = (old_hash, old_mtime, old_ctime)
            continue
        else:
            # hash has changed, update timestamp
            new_timestamps[concept] = (hash, timestamp, old_ctime)
    else:
        if len(old_timestamps) == 0:
            # first run: we don't know anything about history - no timestamps
            new_timestamps[concept] = (hash, '-', '-')
        else:
            # the concept is new, update timestamps

            # check whether the concept already has a created timestamp
            graph_ctime = g.value(concept, DCT.created, None)
            if graph_ctime is not None:
                # there is already a created timestamp in the graph
                # don't try to override it here
                ctime = '-'
            else:
                # no created timestamp in the graph
                # we will set the current timestamp as the ctime
                ctime = timestamp

            new_timestamps[concept] = (hash, timestamp, ctime)

# Add the new timestamps to the graph
for concept, cdata in list(new_timestamps.items()):
    hash, mtime, ctime = cdata
    if mtime != '-':
        g.add((concept, DCT.modified, Literal(mtime, datatype=XSD.date)))
    if ctime != '-':
        g.add((concept, DCT.created, Literal(ctime, datatype=XSD.date)))

# Copy old timestamps that were not in the vocabulary, just in case
# so we don't lose data if the vocabulary is temporarily missing concepts
for concept in old_timestamps:
    if concept not in new_timestamps:
        new_timestamps[concept] = old_timestamps[concept]

# store the new timestamps in the timestamp data file
with open(tsfile, 'w') as f:
    for concept, cdata in sorted(new_timestamps.items()):
        hash, mtime, ctime = cdata
        print("\t".join((concept, hash, mtime, ctime)), file=f)

g.serialize(destination=sys.stdout.buffer, format='turtle')
