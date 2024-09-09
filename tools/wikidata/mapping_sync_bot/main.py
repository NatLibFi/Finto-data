"""Kirjota tähän docstring, kun koodi on valmis"""
import logging # Lokitusta varten
import pprint
from collections import defaultdict
from rdflib import Graph, URIRef, Literal, Namespace, XSD
from sparql_decorator import sparql_query

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

g_yso_trans = Graph()

lines = [
    "<html>",
    "<head><title>Deprekoitu Wikidatassa mutta on YSO:ssa</title></head>",
    "<body>",
    "<h1>Deprekoidut entiteetit</h1>"
]

# === YSO BIG DATA===
SPARQL_QUERY_YSO = """
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
}
"""

ENDPOINT_FINTO = 'http://api.dev.finto.fi/sparql'
params_finto = {'query': SPARQL_QUERY_YSO}
headers = {'User-Agent': 'finto.fi-automation-to-get-yso-mappings-under-dev/0.1.0'}

@sparql_query(endpoint=ENDPOINT_FINTO, params=params_finto, headers=headers, limit=1000)
def process_yso_results(*args):
    """
    Note! def process_yso_results(*args, **kwargs): oli alkuperäinen
    Tee tähän docstring, kun homma vakiintuu

    Parameters:
    
    Returns:
    
    """
    data = args[0]
    g_yso = Graph()

    logging.debug(
        "YSOn tuloksia haettu kaikkiaan: %d",
        len(data['results']['bindings'])
    )

    # with open('raaka_yso_data.txt', 'w') as file:
    #     file.write(pprint.pformat(data))

    for i, result in enumerate(data['results']['bindings']):
        try:
            yso_uri = URIRef(result['s']['value'])
            wikidata_uri = URIRef(result['o']['value'])
            label_lang = result['label'].get('xml:lang', None)
            label = Literal(result['label']['value'], lang=label_lang)

            logging.debug(
                "YSO: Prosessoidaan kohdetta %d: YSO URI=%s, Wikidata URI=%s, Label=%s",
                i + 1, yso_uri, wikidata_uri, label)

            g_yso.add((yso_uri, skos.prefLabel, label))
            g_yso.add((yso_uri, skos.closeMatch, wikidata_uri))

        except KeyError as e:
            logging.error(
                "YSO: Kohteelta %d: puuttuu avain %s",
                i + 1, str(e))

        except ValueError as e:
            logging.error(
                "YSO: Arvoon liittyvä ongelma kohteessa %d: %s",
                i + 1, str(e))

    g_yso.serialize("yso_output.ttl", format="turtle")
    print("YSOn dataa tulostettu tiedostoon yso_output.ttl")

    g_yso_trans = g_yso

process_yso_results()

# === Wikidata BIG DATA ===
SPARQL_QUERY_WIKIDATA = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX pr: <http://purl.org/ontology/prv/core#>
SELECT ?item ?yso ?rank ?statedIn ?subjectNamedAs ?retrieved WHERE {
  ?item p:P2347 ?statement .
  ?statement ps:P2347 ?yso ;
             wikibase:rank ?rank .
  OPTIONAL { 
    ?statement prov:wasDerivedFrom ?derivedFrom .
    ?derivedFrom pr:P248 ?statedIn .
    ?derivedFrom pr:P813 ?retrieved .
  }
  OPTIONAL { ?statement pq:P1810 ?subjectNamedAs . }
}
"""

ENDPOINT_WIKIDATA = 'https://query.wikidata.org/sparql'
params_wikidata = {'query': SPARQL_QUERY_WIKIDATA}
headers_wikidata = {'User-Agent': 'finto.fi-automation-to-get-yso-mappings-under-dev/0.1.0'}

@sparql_query(endpoint=ENDPOINT_WIKIDATA, params=params_wikidata, \
              headers=headers_wikidata, limit=1000)
def process_wikidata_results(*args):
    """
    Note! def process_wikidata_results(*args)(*args, **kwargs): oli alkuperäinen
    Tee tähän docstring, kun homma vakiintuu

    Parameters:
    
    Returns:
    
    """
    data = args[0]
    g_wikidata = Graph()

    logging.debug(
        "Wikidata: Tuloksia haettu kaikkiaan: %d",
        len(data['results']['bindings']))

    with open('raaka_wikidatan_data.txt', 'w') as file:
        file.write(pprint.pformat(data))

    subject_named_as_dict = defaultdict(list)

    for i, result in enumerate(data['results']['bindings']):
        try:
            item = URIRef(result['item']['value'])
            yso_uri = URIRef('http://www.yso.fi/onto/yso/p' + result['yso']['value'])
            rank = URIRef(result['rank']['value'])
            stated_in = URIRef(result['statedIn']['value']) if 'statedIn' in result else None
            retrieved_date = (Literal(result['retrieved']['value'], datatype=XSD.dateTime)
                            if 'retrieved' in result else None)

            if 'subjectNamedAs' in result:
                subject_named_as_dict[item].append(Literal(result['subjectNamedAs']['value']))

            logging.debug(
                "Wikidata: Prosessoidaan kohdetta %d: Item=%s, YSO URI=%s, Rank=%s",
                i + 1, item, yso_uri, rank)

            g_wikidata.add((item, skos.exactMatch, yso_uri))
            g_wikidata.add((item, wikibase.rank, rank))

            if stated_in:
                g_wikidata.add((item, prov.wasDerivedFrom, stated_in))

            for subject_named_as in subject_named_as_dict[item]:
                g_wikidata.add((item, rdfs.label, subject_named_as))

            if retrieved_date:
                g_wikidata.add((item, prov.generatedAtTime, retrieved_date))

        except KeyError as e:
            logging.error(
                "Wikidata: Kohteelta %d: puuttuu avain %s",
                i + 1, str(e))

        except ValueError as e:
            logging.error(
                "Wikidata: Arvoon liittyvä ongelma kohteessa %d: %s",
                i + 1, str(e))

    g_wikidata.serialize("wikidata_output.ttl", format="turtle")
    print("Wikidatan data tallennettu kohteeseen wikidata_output.ttl")

    # Lopputulokset:

    # On deprekoitu Wikidatassa:

    deprecated_in_wikidata_query = """
        SELECT ?entity ?predicate ?object
        WHERE {
            ?entity <http://wikiba.se/ontology#rank> <http://wikiba.se/ontology#DeprecatedRank> .
            ?entity ?predicate ?object .
        }
    """

    g_wikidata_interim_reports = Graph()

    deprecated_in_wikidata_results = g_wikidata.query(deprecated_in_wikidata_query)

    for row in deprecated_in_wikidata_results:
        entity, predicate, object_ = row

        g_wikidata_interim_reports.add((entity, predicate, object_))

        if object_ and str(object_).startswith("http://www.yso.fi/onto/yso/"):
            # print(f"Object {object_} starts with the desired YSO prefix")
            lines.append(f'<p><a href="{object_}">{object_}</a> on deprekoitu Wikidatatan entityssä \
                         <a href="{entity}">{entity}</a>, mutta suhde on edelleen YSOssa</p>')

    lines.append("</body>")
    lines.append("</html>")
    with open('deprekoitu_wikidatassa_mutta_on_ysossa.html', 'w') as file:
        file.write('\n'.join(lines))

    g_wikidata_interim_reports.serialize("wikidata_interim_reports.ttl", format="turtle")
    print("Deprekoituja entiteettejä tallennettu tiedostoon wikidata_interim_reports.ttl")


process_wikidata_results()
