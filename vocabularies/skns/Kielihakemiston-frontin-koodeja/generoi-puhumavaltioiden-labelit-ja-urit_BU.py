#!/usr/bin/env python3

import csv
import requests

INFILE  = "puhumavaltioiden-urit.csv"
OUTFILE = "puhumavaltiot.csv"

ENDPOINT = "https://api.finto.fi/sparql"
GRAPH    = "http://www.yso.fi/onto/yso-paikat/"
LANG     = "fi"

with open(INFILE, encoding="utf-8", newline="") as f:
    uris = [row["uri"].strip() for row in csv.DictReader(f) if row.get("uri")]

values = " ".join(f"<{u}>" for u in uris)
query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?uri ?label WHERE {{
  GRAPH <{GRAPH}> {{
    VALUES ?uri {{ {values} }}
    ?uri skos:prefLabel ?label .
    FILTER(langMatches(lang(?label), "{LANG}"))
  }}
}}
"""

j = requests.post(
    ENDPOINT,
    headers={"Accept": "application/sparql-results+json"},
    data={"query": query},
    timeout=60
).json()

labels = {b["uri"]["value"]: b["label"]["value"] for b in j["results"]["bindings"]}

with open(OUTFILE, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    w.writerow(["uri", "puhumavaltio"])
    for u in uris:
        w.writerow([u, labels.get(u, "")])
