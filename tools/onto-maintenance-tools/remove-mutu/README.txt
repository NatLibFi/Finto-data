Usage: ./remove-mutu.sh <ontology_namespace> <ontology_with_mutu> <output_file>

Removes all MUTU update related triples from the ontology. The script works on turtle ontologies and the output is a TBC compatible turtle ontology.


Requires the script ../tbc-compatibility/make_tbc_compatible.py for making the ontology TBC compatible again.

Uses remove-ns.py, which removes all concepts belonging to one namespace from the ontology.

Requirements: Python, Python rdflib, bash
