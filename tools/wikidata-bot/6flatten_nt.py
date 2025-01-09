import sys
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import XSD

WD = Namespace("http://www.wikidata.org/entity/")
P = Namespace("http://www.wikidata.org/prop/")
PS = Namespace("http://www.wikidata.org/prop/statement/")
PQ = Namespace("http://www.wikidata.org/prop/qualifier/")
PR = Namespace("http://www.wikidata.org/prop/reference/")
PROV = Namespace("http://www.w3.org/ns/prov#")
WIKIBASE = Namespace("http://wikiba.se/ontology#")
YSO = Namespace("http://www.yso.fi/onto/yso/p") # Korjaa: Tämä hassuus pitää poistaa. Syntyi tilanteessa, 
# jossa piti väliaikaisesti synkata outputia ja sen tuottavaa skriptiä keskenään - jäänyt vahingossa tällaiseksi

# Yleistä: Syy miksi raakadata käsitellään alussa NT-tiedostona, mutta muunnetaan sitten turtleksi on se, 
# että blank nodejen serialisointi suoraan Wikidatasta haettaessa turtle-muotoon vaikuttaa olevan melkoisen haasteellista. 
# On helpompaa hakea data aluksi triple kerrallaan ja sitten alkaa muokata nippua ihmisluettavammaksi. Näin usein tehdään, selvittelin.
# Ihmisluettavuuttahan ei periaatteessa tarvita, kun on raportit, mutta debuggauksen kannalta on parempi, että itse datakin on luettavaa. 
# Wikidatan SPARQL endpointti on optimoitu suorituskykyä silmälläpitäen sekä JSON-LD:lle ja N-Tripleille eikä Turtlelle
# Näillä perustelen tämän "inhimillistämisskriptin" olemassaolon.

input_graph = Graph()
output_graph = Graph()

output_graph.bind("wd", WD)
output_graph.bind("p", P)
output_graph.bind("ps", PS)
output_graph.bind("pq", PQ)
output_graph.bind("pr", PR)
output_graph.bind("prov", PROV)
output_graph.bind("wikibase", WIKIBASE)
output_graph.bind("xsd", XSD)
output_graph.bind("yso", YSO)

counter = 0

def increment_counter():
    global counter
    counter += 1

def process_statements():
    # Iteroidaan P2347 (YSO ID)
    for item in input_graph.subjects(predicate=P["P2347"]):
        # Globaaliin input_graphiin sisemmästä skoupista viittaaminen ei "tunnu mukavalta",
        # vaan funktionaalisen paradigman tapa, jossa kaikki funktion käsittelemä tieto passataan argumenttina 
        # fuktiolle, on paljon turvallisempi ja helpommin debugattava tapa, josta ei muodostu mahdollisia ikäviä
        # side effect -ongelmia. Tämä on kuitenkin lopulta kaikkia botin mahdollisesti käyttämiä Python-skriptejä 
        # koskeva kysymys, joten ongelmaa ei kannata vielä tässä kohtaa, ennen kuin isompi kuva mocking-vaiheen 
        # jälkeen on selvillä, yrittää ratkaista.
        
        # Jos P2347 linkittyy blank nodeen, prosessoidaan se
        for statement in input_graph.objects(item, P["P2347"]):
            process_statement(item, statement)

def process_statement(item, statement):
    yso_id = input_graph.value(statement, PS["P2347"])
    rank = input_graph.value(statement, WIKIBASE.rank)
    reference = input_graph.value(statement, PROV.wasDerivedFrom)

    # Qualifierit (jos on) / "subject named as" (P1810)
    literal_values = list(input_graph.objects(statement, PQ["P1810"]))
    
    if reference:
        stated_in = input_graph.value(reference, PR["P248"])
        retrieved_date = input_graph.value(reference, PR["P813"])
    else:
        stated_in = URIRef("http://www.wikidata.org/entity/Q00000000")
        retrieved_date = Literal("2000-01-01T00:00:00+00:00", datatype=XSD.dateTime)
    
    increment_counter()
    add_vocab_data(item, yso_id, rank, reference, literal_values, stated_in, retrieved_date)   
    
        
def add_vocab_data(wikidata_entity, yso_id, rank, reference, literals, stated_in, retrieved_date):
    entity_uri = wikidata_entity

    if yso_id:
        yso_uri = URIRef(f"http://www.yso.fi/onto/yso/p{yso_id}")
        output_graph.add((entity_uri, P["P2347"], yso_uri))

    if rank:
        output_graph.add((entity_uri, WIKIBASE.rank, rank))

    # qualifierit (P1810)
    for literal in literals:
        output_graph.add((entity_uri, PQ["P1810"], Literal(literal)))

    # Referenssitiedot blank nodeilla
    if reference:
        reference_bnode = BNode()  
        output_graph.add((entity_uri, PROV.wasDerivedFrom, reference_bnode))

        if stated_in:
            output_graph.add((reference_bnode, PR["P248"], WD["Q89345680"]))  # YSO-Wikidata mapping project
        if retrieved_date:
            output_graph.add((reference_bnode, PR["P813"], Literal(retrieved_date, datatype=XSD.dateTime)))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 6flatten_nt.py <input_file.ttl> <output_file.ttl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    input_graph.parse(input_file, format="turtle")
    
    process_statements()

    with open(output_file, "w") as f:
        f.write(output_graph.serialize(format="turtle"))

    print(f"Vocabulary data has been written to {output_file}")
    print(counter)
