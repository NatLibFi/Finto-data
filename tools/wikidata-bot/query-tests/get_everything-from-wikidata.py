from SPARQLWrapper import SPARQLWrapper, RDFXML
from rdflib import Graph, URIRef, Namespace

endpoint_url = "https://query.wikidata.org/sparql"

query = """
    CONSTRUCT {
        ?wikidataItem <http://www.wikidata.org/prop/direct/P2347> ?ysoConcept .
        ?wikidataItem <http://www.w3.org/2000/01/rdf-schema#label> ?wikidataLabel .
    }
    WHERE {
        ?wikidataItem wdt:P2347 ?ysoConcept .
        OPTIONAL { ?wikidataItem rdfs:label ?wikidataLabel FILTER(LANG(?wikidataLabel) = "en") }
        OPTIONAL { ?ysoConcept rdfs:label ?ysoLabel FILTER(LANG(?ysoLabel) = "fi") }
    }
"""

sparql = SPARQLWrapper(endpoint_url)
sparql.setQuery(query)
sparql.setReturnFormat(RDFXML)

rdf_data = sparql.query().convert()

graph = Graph()
graph.parse(data=rdf_data.serialize(format="xml"), format="xml")

wdt_p2347 = URIRef("http://www.wikidata.org/prop/direct/P2347")

for s, p, o in list(graph.triples((None, wdt_p2347, None))):
    if o.startswith("http://www.wikidata.org/entity/Q"):
        continue
    new_uri = URIRef(f"http://www.yso.fi/onto/yso/p{o}")
    graph.remove((s, p, o))
    graph.add((s, p, new_uri))

output_file = "wikidata_ysomap.ttl"
graph.serialize(destination=output_file, format="turtle", encoding="utf-8")

print(f"✅ Wikidatan YSO-mäppäykset tallennettu tiedostoon {output_file}")
