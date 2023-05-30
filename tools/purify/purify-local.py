#!/usr/bin/env python3

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
##
## Modified 28.3.2023 by Joeli Takala <joeli.takala@helsinki.fi>:
## * Changed Python 2 method calls to their Python 3 equivalents
## * Changed Python 2 library imports to their Python 3 equivalents
## * Changed Python 2 comparison operators to their Python 3 equivalents
## * Changed the UTF-8 encoding from specific URIs to UTF-8 encoding of HTTP responses
## * Changed the serialization destination of the rdflib model
##
## Modified 2023-05-29 by Osma Suominen <osma.suominen@helsinki.fi>:
## * Modernized use of rdflib. No need to support rdflib < 6 anymore.
## * Removed the dependency on the puri.onki.fi service, using local TSV file instead.
## * Removed status output (printing of . and s symbols)


from optparse import OptionParser
import sys
try:
  from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace
except ImportError:
  print("You need to install the rdflib Python library (http://rdflib.net).", file=sys.stderr)
  print("On Debian/Ubuntu, try: sudo apt-get install python3-rdflib", file=sys.stderr)
  sys.exit(1)
      
import re
import datetime


## Define functions

def _getpuri(uri, nsto):
  global puris, maxcounter

  if uri not in puris:
    puri = nsto + str(maxcounter)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    puris[uri] = (puri, ts)
    sys.stderr.write(f"Coined PURI {puri} for {uri}\n")
    maxcounter += 1

  return URIRef(puris[uri][0])


def getpuri(uri, nsfrom, nsto, skippuris):
  res = None

  if (isinstance(uri, URIRef) and uri.startswith(nsfrom) and len(uri) > len(nsfrom)):

    if (skippuris is not None and uri.startswith(nsfrom+skippuris) and
        uri[len(nsfrom+skippuris):] != "" and
        uri[len(nsfrom+skippuris):].isdigit()):

      return uri
    else:
      res = _getpuri(str(uri), nsto)

  return res


def load_puris(purifile):
  puris = {}
  with open(purifile) as purif:
    for line in purif:
      uri, puri, ts = line.strip().split("\t")
      puris[uri] = (puri, ts)

  return puris

def save_puris(purifile, puris):
  with open(purifile, 'w') as purif:
    for uri, (puri, ts) in puris.items():
      print(f"{uri}\t{puri}\t{ts}", file=purif)


###############################################################

## Parse command line

parser = OptionParser(usage="%prog [options] file sourceNS targetNS purifile")
parser.add_option('-f', '--from-format',
        help='input format (xml, trix, n3, nt, turtle, rdfa), defaults to xml', default='xml')
parser.add_option('-t', '--to-format',
        help='output format (xml, trix, n3, nt, turtle), defaults to xml', default='xml')
parser.add_option('-s', '--skip-existing-puris', 
        help='input: puri-prefix, skips existing PURIs in the source namespace', default=None)
parser.add_option('-C', '--puri-counter-start-value', 
        help='input: counter start value', default=None)

(options, args) = parser.parse_args()

if len(args) < 4:
  parser.print_help()
  print ("\nExample: purify.py myonto.owl \"http://www.yso.fi/onto/myonto/\" \"http://www.yso.fi/onto/myonto/m\" puri-mappings.tsv")
  sys.exit(1)

file = args[0]
nsfrom = args[1]
nsto = args[2]
purifile = args[3]

## Set skip puri NS

skippuris = options.skip_existing_puris

## Load PURI database from file

puris = load_puris(purifile)

## Load to RDF model

m = Graph()
if file == '-':
    m.parse(sys.stdin, format=options.from_format)
else:
    m.parse(file, format=options.from_format)

## Set puri counter start value

if (options.puri_counter_start_value is not None):
  maxcounter = int(options.puri_counter_start_value)
else:
  sys.stderr.write("Searching for PURI counter maximum...")

  maxcounter=-1
  for stmt in list(m.triples((None, None, None))):
    for uri in stmt:
      if (isinstance(uri, URIRef) and uri.startswith(nsto) and
          uri[len(nsto):] != "" and
          uri[len(nsto):].isdigit()):
        if (int(maxcounter) < int(uri[len(nsto):])):
          maxcounter = int(uri[len(nsto):])
  maxcounter = maxcounter + 1

sys.stderr.write("Set PURI counter to %s\n" % maxcounter)


## change each subject

sys.stderr.write("Modifying the triples...\n")

for s,p,o in list(m.triples((None, None, None))):
  s2 = None
  p2 = None
  o2 = None

  if (s is None or
      p is None or
      o is None):
    continue

  s2 = getpuri(s, nsfrom, nsto, skippuris)
  p2 = getpuri(p, nsfrom, nsto, skippuris)
  o2 = getpuri(o, nsfrom, nsto, skippuris)

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


sys.stderr.write("\n")
m.serialize(destination=sys.stdout.buffer, format=options.to_format)

## Write the (possibly) modified PURI database to the PURI file

save_puris(purifile, puris)
