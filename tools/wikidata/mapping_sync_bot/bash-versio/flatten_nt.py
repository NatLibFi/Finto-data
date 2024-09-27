import sys
from rdflib import Graph

def flatten_rdf_to_ttl(input_file, output_file):
    g = Graph()
    print(f"Parsing {input_file}...")
    g.parse(input_file, format="nt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix p: <http://www.wikidata.org/prop/> .
@prefix ps: <http://www.wikidata.org/prop/statement/> .
@prefix pq: <http://www.wikidata.org/prop/qualifier/> .
@prefix pr: <http://www.wikidata.org/prop/reference/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix wikibase: <http://wikiba.se/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

""")
        for subj in set(g.subjects()):
            f.write(f"{subj.n3(g.namespace_manager)}\n")

            for pred, obj in g.predicate_objects(subj):
                if "statement" in obj and "P2347" in pred:
                    f.write(f"    {pred.n3(g.namespace_manager)} [\n")

                    for stmt_pred, stmt_obj in g.predicate_objects(obj):
                        f.write(f"        {stmt_pred.n3(g.namespace_manager)} {stmt_obj.n3(g.namespace_manager)} ;\n")
                    
                    f.write("    ] ;\n")

                else:
                    f.write(f"    {pred.n3(g.namespace_manager)} {obj.n3(g.namespace_manager)} ;\n")

            f.write(".\n\n")

    print(f"Konversio suoritettu: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kutsu: python flatten_rdf_to_ttl.py <input_file.nt> <output_file.ttl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    flatten_rdf_to_ttl(input_file, output_file)
