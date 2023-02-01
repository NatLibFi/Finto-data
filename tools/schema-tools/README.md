Scripts for converting RDF data model to HTML and mapping data model property URIs to URNs.

Usage example of converting data model to HTML: 
```
python rdf_to_html.py -pl="skos:prefLabel" -l="fi" -i="ntp" -o="ntp.html" -u="https://github.com/NatLibFi/ntp-model/tree/master/elementset/ntp#"
```

Usage example of mapping property URIs with URNs to XML file (to validate XML use parameter -v and XSD file from http://epc.ub.uu.se/schema/rs/3.0/rs-location-mapping-schema.xsd)
```
python html_urn_mapping.py -ns="URN:NBN:fi:schema:ntp:" -p="http://schema.finto.fi/ntp#" -i"ntp.ttl" -o="testi.xml"
```

Copyright: © the National Library of Finland, 2021

License: The software source code is licensed under a GNU, General Public License, Version 3.0.
