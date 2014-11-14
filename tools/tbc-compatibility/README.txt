*** prote2tbc.sh ***

Script for making an owl ontology used in Protege to the form supported by TopBraid Composer (TBC) ontology editor.
The script splits a combined ontology to the domain ontology and to the general ontology. After this, both of the files are modified for TBC combatibility.

Note: create a new configuration file for the domain ontology. The configuration file for YSO is already done, but you might need to add some properties to it due to the unstandardised FinnONTO namespaces.

Requirements:
ontorip (../ontorip/ontorip.py)
bash
python 2.7

Usage:

./prote2tbc <domain-name> <input-onto-path> <config-file-dir> <dir-for-domain-and-general>
./prote2tbc.sh kauno ~/files/kauno.owl config/ ~/files/


*** ensure_tbc_combatibility.py ***

Ensures that the properties of the ontology are compatible with the properties that are used for showing labels of concepts and searching in TBC.
Changes the labels of the ontology to SKOS, adds an owl:Ontology instance to the ontology and removes unnecessary properties from the ontology.

Requirements:
python 2.7

Usage:

./ensure_tbc_combatibility.py <config-file> <input-onto> <output-onto>
./ensure_tbc_combatibility.py config/kauno.prop ~/files/kauno-ontorip.ttl ~/files/kauno-tbc.ttl


*** add_baseuri.py ***

Adds an additional line to the beginning of file stating the baseURI for the file. This enables viewing and modificating the metadata of the ontology in TBC.

Requirements:
python 2.7

Usage:

./add_baseuri.py ~/files/kauno-tbc.ttl 'http://www.yso.fi/onto/kauno/' > ~/files/kauno.ttl
