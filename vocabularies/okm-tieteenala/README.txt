OKM:n tieteenalaluokitus 26.11.2010

OKM on julkaissut luokituksen ainoastaan PDF-tiedostona. Tässä hakemistossa
on muunnin, joka raapii PDF:stä irti luokituksen ja esittää sen SKOSina.

Käyttö:
./toskos.sh

Huomioita muunnoksesta:

URIt on muodostettu luokkakoodeista. URIn localname on "ta" + koodinumero
ilman pilkkua. Alkuperäinen luokkakoodi on tallella skos:notation-arvona.

Ylätason luokat ovat tässä muunnoksessa tavallisia SKOS Concepteja, vaikka
niitä todennäköisesti ei ole tarkoitus käyttää kuvailussa.

Luokitus on hieman laajennettu versio Tilastokeskuksen
tieteenalaluokituksesta. Olisi fiksua esittää sekin SKOSina ja suhteet
näiden luokitusten välillä SKOS Mappingilla, jos TK:n luokitusta käytetään
jossain.
