*** prote2tbc.sh ***

Script for making an owl ontology used in Protege to the form supported by TopBraid Composer (TBC) ontology editor.
The script splits a combined ontology to the domain ontology and to the general ontology. After this, both of the files are modified for TBC combatibility.

Requirements:
ontorip (Finto-data/tools/ontorip/ontorip.py)
bash
python 2.7

Usage:

./prote2tbc <domain-name> <input-onto-path> <config-file> <dir-for-domain-and-general>



*** ensure_tbc_combatibility.py ***

Ensures that the properties of the ontology are compatible with the properties that are used for showing labels of concepts and searching in TBC.
Changes the labels of the ontology to SKOS, adds an owl:Ontology instance to the ontology and removes unnecessary properties from the ontology.

Usage:

./ensure_tbc_combatibility.py <config-file> <input-onto> <output-onto>
./ensure_tbc_combatibility.py config/kauno.prop ~/files/kauno-ontorip.ttl ~/files/kauno-tbc.ttl


*** add_baseuri.py ***

Adds an additional line to the beginning of file stating the baseURI for the file. This enables viewing and modificating the metadata of the ontology in TBC.

Usage:

./add_baseuri.py ~/files/kauno-tbc.ttl 'http://www.yso.fi/onto/kauno/' > ~/files/kauno.ttl
