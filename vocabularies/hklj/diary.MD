## Päivitys 26.1.2024

1) Originaalin varmistaminen: mv hklj-tbc2.ttl hklj-tbc2-orig.ttl

2) TBC:n omat triplet pois tekstieditorissa: hklj-tbc2-orig.ttl 
--> hklj-tbc2-prujut-pois.ttl

3) Validointi: riot --validate hklj-tbc2-prujut-pois.ttl 
--> hklj-tbc2-validated.ttl

4) Unixaaminen: dos2unix hklj-tbc2-validated.ttl 
--> hklj-tbc2-unixattu.ttl 

5) Toskos.sh:ta varten uudelleen nimeäminen: mv hklj-tbc2-unixattu.ttl hklj.ttl
--> hklj.ttl

6) Skossaamminen: ./toskos.sh hklj.ttl
--> hklj-skos.ttl

7) Testaaminen lokaalissa Fusekissa/Skosmoksessa: s-put http://localhost:3030/skosmos/data http://urn.fi/URN:NBN:fi:au:hklj: hklj-skos.ttl 
--> ok!

8) Upstreamiin lataaminen: / pullaus / stagingiin lisääminen / commit kommentilla / push

9) Devillä testaaminen: https://dev.finto.fi/hklj/fi/page/f1
--> Kaunoluokassa vastaavussuhde skos:closeMatch YKL:ään lisätty - ok!

19) Tiedottaminen seuraavana arkipäivänä, kun on päivittynyt Fintoon