#!/usr/bin/env python

## purify.py
## Kim Viljanen, 1.10.2010
##
## Purify replaces URIs in a given namespace and replaces them with
## persistent URIs (aka PURI) which are fetched from the PURI registry
## located at (e.g.) http://puri.onki.fi.
##
## Modified by Osma Suominen <osma.suominen@helsinki.fi>:
## * fix rdflib 4.0 incompatibility by wrapping triples() results in list()
## * add -t (TO_FORMAT) argument
## * more efficient serializing (output to sys.stdout directly, not via print)
## * avoid purifying the namespace URI itself (often a owl:Ontology instance)

from optparse import OptionParser
import sys
try:
  from rdflib import URIRef, Literal, RDF, RDFS, Namespace
except ImportError:
  print >>sys.stderr, "You need to install the rdflib Python library (http://rdflib.net)."
  print >>sys.stderr, "On Debian/Ubuntu, try: sudo apt-get install python-rdflib"
  sys.exit(1)
      
try:
  # rdflib 2.4.x
  from rdflib.Graph import Graph
  m = Graph('Memory')

except ImportError:
  # rdflib 3.x
  from rdflib import Graph
  m = Graph()

import httplib, urllib
import re


## Define functions

def getpuri(uri, nsfrom, nsto, context, skippuris):
  res = None

  if (isinstance(uri, URIRef) and uri.startswith(nsfrom) and len(uri) > len(nsfrom)):

    if (skippuris is not None and uri.startswith(nsfrom+skippuris) and 
        uri[len(nsfrom+skippuris):] is not "" and 
        uri[len(nsfrom+skippuris):].isdigit()):

      sys.stderr.write("s") 
###Skipped puri: %s\n" % (uri))
      return uri
    else:

      ## caching
      if (uri in uricache and nsto in uricache[uri]):
        return uricache[uri][nsto]

      res = puridb_call('getpuri', {'uri':uri.encode('UTF-8'), 'purins':nsto, 'context':context})
      res = URIRef(res)

      ## caching
      if (uri not in uricache):
        uricache[uri]={}
      uricache[uri][nsto] = res

  return res


def puridb_call(method, params):

  params = urllib.urlencode(params)

  conn = httplib.HTTPConnection(puridb)
  conn.request("GET", "/%s?%s" % (method, params))

  response = conn.getresponse()

  if (response.status != 200):
    print "puridb_call: ERROR: "
    print response.read()
    sys.exit(1)

  res = response.read()
  conn.close()

  return res


###############################################################



## Settings

puridb = "puri.onki.fi"


## Parse command line

parser = OptionParser(usage="%prog [options] file sourceNS targetNS")
parser.add_option('-f', '--from-format',
        help='input format (xml, trix, n3, nt, turtle, rdfa), defaults to xml', default='xml')
parser.add_option('-t', '--to-format',
        help='output format (xml, trix, n3, nt, turtle), defaults to xml', default='xml')
parser.add_option('-s', '--skip-existing-puris', 
        help='input: puri-prefix, skips existing PURIs in the source namespace', default=None)
parser.add_option('-C', '--puri-counter-start-value', 
        help='input: counter start value', default=None)
parser.add_option('-c', '--context', 
        help='sets the context ID', default=None)

(options, args) = parser.parse_args()

if len(args) < 3:
  parser.print_help()
  print "\nExample: purify.py -c \"http://www.yso.fi/onto/myonto/m\" myonto.owl \"http://www.yso.fi/onto/myonto/\" \"http://www.yso.fi/onto/myonto/m\""
  sys.exit(1)

file = args[0]
nsfrom = args[1]
nsto = args[2]

## Context ID

context = nsto

if (options.context is not None):
  context = options.context


## Set skip puri NS

skippuris = options.skip_existing_puris


## Cache
uricache = {}

## Load to RDF model

if file == '-':
    m.parse(sys.stdin, format=options.from_format)
else:
    m.parse(file, format=options.from_format)

## Set puri counter start value

if (options.puri_counter_start_value is not None):
  if (not options.puri_counter_start_value.isdigit()):
    sys.stderr.write("Searching for PURI counter maximum...")

    statusc=0
    maxcounter=-1
    for stmt in list(m.triples((None, None, None))):
      for uri in stmt:
        if (isinstance(uri, URIRef) and uri.startswith(nsto) and
            uri[len(nsto):] is not "" and 
            uri[len(nsto):].isdigit()):
          if (int(maxcounter) < int(uri[len(nsto):])):
            maxcounter = int(uri[len(nsto):])
        statusc = statusc + 1
        if (statusc % 1000 == 0):
          sys.stderr.write(".")
    maxcounter = maxcounter + 1
  else:
    maxcounter = int(options.puri_counter_start_value)

  puridb_call('setcounter', {'purins':nsto, 'counter':maxcounter})

  sys.stderr.write("\n")
  sys.stderr.write("Set PURI counter for ns %s to %s\n" % (nsto, maxcounter))


## change each subject

statusc=0

sys.stderr.write("Modifying the triplets...")

for s,p,o in list(m.triples((None, None, None))):
  s2 = None
  p2 = None
  o2 = None

  if (s is None or
      p is None or
      o is None):
    continue

  s2 = getpuri(s, nsfrom, nsto, context, skippuris)
  p2 = getpuri(p, nsfrom, nsto, context, skippuris)
  o2 = getpuri(o, nsfrom, nsto, context, skippuris)

  if (s2 is None):
    s2 = s
  if (p2 is None):
    p2 = p
  if (o2 is None):
    o2 = o

  if (s is not s2 or
      p is not p2 or
      o is not o2):

    m.remove((s, p, o))
    m.add((s2, p2, o2))

  statusc = statusc + 1
  if (statusc % 1000 == 0):
    sys.stderr.write(".")


sys.stderr.write("\n")
m.serialize(destination=sys.stdout, format=options.to_format)
