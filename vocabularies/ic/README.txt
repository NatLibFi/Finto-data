Downloaded on 2014-01-09 from
http://iconclass.org/data/iconclass.20121019.nt.gz
and uncompressed.

Edited to fix parsing problems (newlines in string literals).

The file has to be interpreted as Turtle, because it contains unescaped,
UTF-8 encoded characters which are not allowed in N-Triple syntax and
cannot be parsed by rdflib.

References to concepts that contain no information (e.g. no rdf:type)
are stripped from the output using the strip-untyped-concepts.py script.

According to http://www.iconclass.org/help/lod :
ICONCLASS is made available under the Open Database License:
http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual
contents of the database are licensed under the Database Contents License:
http://opendatacommons.org/licenses/dbcl/1.0/ 
