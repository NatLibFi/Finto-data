#!/usr/bin/env python3

from rdflib import *
import sys
import logging

if len(sys.argv) != 3:
  print("Usage: ./mesh-updater.py mesh-sv-en.ttl Master_MeSH_FinMeSH_updated.txt")
  sys.exit(1)

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s %(levelname)s %(message)s',
  handlers=[
    logging.FileHandler('mesh-updater.log', mode='w', encoding='utf-8')
  ]
)

logger = logging.getLogger(__name__)

g = Graph()
out = Graph()

try:
  g.parse(sys.argv[1]) #mesh-sv-en
except FileNotFoundError:
  logger.exception("Error: Tiedostoa '%s' ei löytynyt." % (sys.argv[1]))
  sys.exit(1)

prefSuccess = 0
prefFail = 0
altSuccess = 0
altFail = 0

with open(sys.argv[2], 'r') as labels:
  conceptLabels = []
  for line in (*labels, ""):  # adding extra empty line in the end
    line = line.strip()
    if line == "":
      if conceptLabels:
        enLabel = conceptLabels[0]
        finLabel = conceptLabels[1]
        finAltLabelArr = conceptLabels[2:]

        enPref = Literal(enLabel, lang="en")
        concept = g.value(predicate=SKOS.prefLabel, object=enPref, any=False)

        if concept is None:
          logger.warning("MeSH-tunnistetta ei löytynyt labelille \"" + enLabel + "\"@en")
          prefFail += 1
          altFail += len(finAltLabelArr)
        else:
          finPref = Literal(finLabel, lang="fi")
          out.add((concept, SKOS.prefLabel, finPref))
          prefSuccess += 1

          for finAltLabel in finAltLabelArr:
            finAlt = Literal(finAltLabel, lang="fi")
            out.add((concept, SKOS.altLabel, finAlt))
            altSuccess += 1

        conceptLabels = []
    else:
      conceptLabels.append(line)


logger.info("Tallennettu MeSH-tunnisteiden alle %skpl suomenkielisiä prefLabeleita" % prefSuccess)
logger.info("Tallennettu MeSH-tunnisteiden alle %skpl suomenkielisiä altLabeleita" % altSuccess)
logger.info("%skpl suomenkielisiä prefLabeleita ei löytänyt sopivaa MeSH-tunnistetta" % prefFail)
logger.info("%skpl suomenkielisiä altLabeleita ei löytänyt sopivaa MeSH-tunnistetta" % altFail)

out.serialize(destination=sys.stdout.buffer, format='turtle')
