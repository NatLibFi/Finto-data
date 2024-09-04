import logging
from sparql_decorator import sparql_query
from rdflib import Graph, URIRef, Literal, Namespace, XSD

logging.basicConfig(level=logging.DEBUG)

skos = Namespace("http://www.w3.org/2004/02/skos/core#")
yso = Namespace("http://www.yso.fi/onto/yso/")
wd = Namespace("http://www.wikidata.org/entity/")
p = Namespace("http://www.wikidata.org/prop/")
ps = Namespace("http://www.wikidata.org/prop/statement/")
prov = Namespace("http://www.w3.org/ns/prov#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
wikibase = Namespace("http://wikiba.se/ontology#")
pr = Namespace("http://www.wikidata.org/prop/reference/")

# === YSO ===
sparql_query_yso = """
PREFIX yso: <http://www.yso.fi/onto/yso/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?s ?o ?label
WHERE {
    GRAPH <http://www.yso.fi/onto/yso/> {
        ?s skos:closeMatch ?o .
        ?s skos:prefLabel ?label .
        OPTIONAL {?s skos:exactMatch ?o .}
        FILTER regex(str(?s), "^http://www.yso.fi/onto/yso/")
        FILTER(STRSTARTS(STR(?o), "http://www.wikidata.org"))
    }
} LIMIT 10000
"""

endpoint_finto = 'http://api.dev.finto.fi/sparql'
params_finto = {'query': sparql_query_yso}
headers = {'User-Agent': 'finto.fi-automation-to-get-yso-mappings/0.1.0'}

@sparql_query(endpoint=endpoint_finto, params=params_finto, headers=headers)
def process_yso_results(data):
    g_yso = Graph()

    logging.debug(f"YSOn tuloksia haettu kaikkiaan: {len(data['results']['bindings'])}")

    for i, result in enumerate(data['results']['bindings']):
        try:
            yso_uri = URIRef(result['s']['value'])
            wikidata_uri = URIRef(result['o']['value'])
            label_lang = result['label'].get('xml:lang', None)
            label = Literal(result['label']['value'], lang=label_lang)

            logging.debug(f"YSO: Prosessoidaan kohdetta {i + 1}: YSO URI={yso_uri}, Wikidata URI={wikidata_uri}, Label={label}")

            g_yso.add((yso_uri, skos.prefLabel, label))
            g_yso.add((yso_uri, skos.closeMatch, wikidata_uri))
        except Exception as e:
            logging.error(f"YSO: Virhe käsiteltäessä kohdetta {i + 1}: {e}")

    g_yso.serialize("yso_output.ttl", format="turtle")
    print("YSOn dataa tulostettu tiedostoon yso_output.ttl")

process_yso_results()

# === Wikidata ===
sparql_query_wikidata = """
SELECT ?item ?yso ?rank ?statedIn ?subjectNamedAs ?retrieved WHERE {
  ?item p:P2347 ?statement .
  ?statement ps:P2347 ?yso ;
             wikibase:rank ?rank .
  OPTIONAL { 
    ?statement prov:wasDerivedFrom ?derivedFrom .
    ?derivedFrom pr:P248 ?statedIn .
    ?derivedFrom pr:P813 ?retrieved .
  }
  OPTIONAL { ?statement rdfs:label ?subjectNamedAs . }
} LIMIT 9999
"""

endpoint_wikidata = 'https://query.wikidata.org/sparql'
params_wikidata = {'query': sparql_query_wikidata}
headers_wikidata = {'User-Agent': 'finto.fi-automation-to-get-yso-mappings/0.1.0'}

@sparql_query(endpoint=endpoint_wikidata, params=params_wikidata, headers=headers_wikidata)
def process_wikidata_results(data):
    g_wikidata = Graph()

    logging.debug(f"Wikidata: Tuloksia haettu kaikkiaan: {len(data['results']['bindings'])}")

    for i, result in enumerate(data['results']['bindings']):
        try:
            item = URIRef(result['item']['value'])
            yso_uri = URIRef('http://www.yso.fi/onto/yso/p' + result['yso']['value'])
            rank = URIRef(result['rank']['value'])
            stated_in = URIRef(result['statedIn']['value']) if 'statedIn' in result else None
            subject_named_as = Literal(result['subjectNamedAs']['value']) if 'subjectNamedAs' in result else None
            retrieved_date = Literal(result['retrieved']['value'], datatype=XSD.dateTime) if 'retrieved' in result else None

            logging.debug(f"Wikidata: Prosessoidaan kohdetta {i + 1}: Item={item}, YSO URI={yso_uri}, Rank={rank}")

            g_wikidata.add((item, skos.exactMatch, yso_uri))
            g_wikidata.add((item, wikibase.rank, rank))
            if stated_in:
                g_wikidata.add((item, prov.wasDerivedFrom, stated_in))
            if subject_named_as:
                g_wikidata.add((item, skos.altLabel, subject_named_as))
            if retrieved_date:
                g_wikidata.add((item, prov.generatedAtTime, retrieved_date))

        except Exception as e:
            logging.error(f"Wikidata: Virhe prosessoitaessa kohdetta {i + 1}: {e}")

    g_wikidata.serialize("wikidata_output.ttl", format="turtle")
    print("Wikidatan data tallennettu kohteeseen wikidata_output.ttl")

process_wikidata_results()
