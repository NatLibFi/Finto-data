Converts a file to TBC acceptible format by adding a baseURI declaration in the beginning of a file.
This allows the modification of the ontology details in TBC.

Used only with Turtle (.ttl files), no guarantee with other file types.

Usage example:

./make_tbc_compatible.py test-ontology.ttl 'http://www.yso.fi/onto/yso/' > tbc-compatible-onto.ttl
