
# Tässä teknisen ylläpidon alkupohdintoja

## Kehitysversio

- Julkaisutiedoston 269 skos:Collection- ja isothes:ConceptGroup-rresurssia ovat kehitysmallin eksometa:ThematicGroup:in SKOS-mallin mukainen muoto

- Löytyy myös eksometa:hasThematicGroup, joka muunnetaan kehityksen ja tuotannon välillä klassisesti näin:<br>
käsite - eksometa:hasThematicGroup -> ryhmä<br>
ryhmä - skos:member -> käsite

- owl:equivalentClass (kehitys) -> skos:exactMatch (julkaisu)

- rdfs:subClassOf (kehitys) -> skos:broader (julkaisu). Kehityksessä on 4 112 ekso->YSO-rdfs:subClassOf -suhdetta, mutta julkaisuversiossa 4 088 ekso->YSO-skos:broader-suhdetta. Ero saattaa olla skosifyn tuottamaa, pitää tutkia myöhemmin tarkemmin

- Luokalla ekso-meta:Hierarchy (on myös skos:Concept) on kuusi instanssia, mutta sitä ei ole eksplisiittieseti määritelty. 

- Toimituksellista ylläpidon tarvitsemaa metadataa on melko paljon:
eksometa:status
eksometa:date
eksometa:dt
eksometa:source
eksometa:type
skos:editorialNote
Nämä toki poistetaan julkaisuvaiheessa

- Myös http://www.yso.fi/onto/ekso-vanhat/ katoaa julkaisussa


## Julkaisuversio

- Ekso-käsitteitä on 3 985

- Ryhmittely samanaikaisesti skos:Collection- ja isothes:ConceptGroup-rakenteilla eli skosin puolesta tosiaan vain kokoelma, mutta käsiteryhmä selvästi ryhmittelee aihealueiden perusteella. 

- On määritelty eksometa:ThematicGroup ja se on eksometa:svLabel:in domain, mutta käytännössä sillä ei ole ainuttakaan instanssia.

- Ekso ripustuu YSOon "normaalisti" skos:broader-suhteilla, mutta samalla käsitteillä on mahdollisesti myös ekvivalenssi (skos:exactMatch) YSOn vastaaviin käsitteisiin (jakavat siis samat YSOn yläkäsitteet, ekso-käsite ja mäpätty YSO-käsite). Ekson "hovioikeudet" broader -> "yleiset tuomioistuimet" <exactMatch> YSOn "hovioikeudet" broader -> "tuomioistuimet" eli pientä nyanssieroa yläkäsitesuhteiden välillä saattaa ilmetä, mutta ei liene ongelma muuten kuin tarkan ylläpitotyön osalta voi olla tarkkuutta vaativaa hommaa, maybe.

- YSOn käsitteet ovat totuttuun tapaan YSO-käsitteitä (tietenkin), mutta ne ovat käytännössä osa ekson käsitejärjestelmää skeemojen kautta eli kuuluvat skeemaan ekso:, mutta myös tapauskohtaisesti skeemoihin ekso:aggregateconceptscheme ja ekso:deprecatedconceptscheme.

- Kolmikielisenä sanastona kielten osalta suomen ja englannin suhteen sanasto on täydellinen eli käsitteiden prefLabelit löytyvät molemmilla kielillä, mutta yhdeksältä käsitteeltä puuttuu ruotsinkielinen prefLAbel:  
ekso:p174<br>
ekso:p720<br>
ekso:p875<br>
ekso:p1583<br>
ekso:p2209<br>
ekso:p3017<br>
ekso:p3316<br>
ekso:p3721<br>
ekso:p4211<br>
Ryhmältä ja kokoelmalta ekso:p1214 puuttuu ruotsinkielinen prefLabel

- Mielenkiintoinen kieliystävällisyyttä ja saavutettavuutta lisäävä tekijä on eksometa:svLabel (rdfs:comment "RIIKINRUOTSALAINEN VASTINE"@fi), jota on hyödynnetty 24 käsitteessä.

- Kielten tasapaino kuitenkin järkkyy (tai on vain suomi-painotteinen) muiden kuin prefLabeleiden osalta
			fi 		sv 		en
altLabel	1 558	133		795
hiddenLabel	130		8		8
note		309		0		0

## Pohdintoja/kommentteja:

- Nyt eksoa on ylläpidetty TBC:ssä, miten veebeistäminen hoidetaan?
- Perusjuttu näyttää melko selvältä ja suoraviivaiselta
- En usko, että mitään isompaa ongelmaa julkaisun kassa tulee, pitää vain olla huolellinen päivityksen suunnittelussa.








