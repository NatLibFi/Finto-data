{# This is the template for the about page. You can enter any html here and show different language versions by using the lang value in a twig conditional as demonstrated below. #}
{% if lang == 'fi' %}
<h4>Tietoja</h4>
<p>Finto on suomalainen palvelu sanastojen, ontologioiden ja luokitusten julkaisua ja käyttöä varten. Finto tarjoaa käyttöliittymän sanastojen selailulle, sekä avoimet rajapinnat sanastojen hyödyntämiseen muissa sovelluksissa.</p>
<p>Fintoa kehitetään Kansalliskirjaston, opetus- ja kulttuuriministeriön ja valtiovarainministeriön yhteisessä <a href="http://wiki.helsinki.fi/display/ONKI/">ONKI-projektissa.</a></p>

<p>ONKI-projekti jatkaa Aalto-yliopistossa ja Helsingin yliopistossa vuosina 2003 - 2012 toimineen  <a href="http://www.seco.tkk.fi/projects/finnonto/index.fi.php/">FinnONTO-hankkeen työtä.</a></p>

<p>Jos kohtaat ongelmia tai sinulla on kehitysideoita palvelun suhteen, ota yhteyttä Finton kehittäjiin. Olemme myös erittäin kiinnostuneita sinun menestystarinoistasi Finton käytössä - <a href="../fi/feedback">jaa kokemuksiasi meille ja muille!</a></p>      

<h4>Linkkejä</h4>
<a href="http://wiki.helsinki.fi/display/ONKI/">ONKI-projektin Wikisivu.</a><br />
<a href="http://www.seco.tkk.fi/">Semanttisen laskennan tutkimusryhmä SeCo</a><br />
<a href="http://www.kansalliskirjasto.fi/">Kansalliskirjasto</a><br />
{% elseif lang == 'sv' %}
<h4>Information</h4>
<p>Finto är en finländsk service för publicering och användning av tesaurusar, ontologier och klassifikationer. Finto erbjuder ett användargränssnitt för direkt användning av vokabulärerna och öppna gränssnitt för användning i andra applikationer.</p>
<p>Finto utvecklas i ONKI-projektet, som är ett gemensamt projekt mellan Nationalbiblioteket, Undervisnings- och kulturministeriet och Finansministeriet: <a href="http://wiki.helsinki.fi/display/ONKI/">ONKI-projektets wikisida</a></p>

<p>ONKI-projektet fortsätter det arbete som gjorts i FinnONTO-projektet vid Aalto-universitetet och Helsingfors universitet under åren 2003-2012:<a href="http://www.seco.tkk.fi/projects/finnonto/index.fi.php/">FinnONTO</a></p>

<p>Ta kontakt med utvecklarna av Finto om du stöter på problem eller om du har utvecklingsidéer gällande servicen. Vi är också mycket intresserade av dina framgångar med användningen av Finto -<a href="../sv/feedback"> dela dina erfarenheter med oss och med andra!</a></p>      

<h4>Länkar</h4>
<a href="http://wiki.helsinki.fi/display/ONKI/">ONKI-projektets wikisida</a><br />
<a href="http://www.seco.tkk.fi/">Forskningsgruppen för semantisk beräkning SeCo</a><br />
<a href="http://www.kansalliskirjasto.fi/">Nationalbiblioteket</a><br />
{% elseif lang == 'en' %}
<h4>About</h4>
<p>Finto is a Finnish service for the publication and utilization of vocabularies, ontologies and classifications. It provides a user interface for browsing the vocabularies and open interfaces for utilizing them in other applications.</p>
<p>Finto is being developed as a joint project between the National Library of Finland, the Ministry of Finance, and the Ministry of Education and Culture. <a href="http://wiki.helsinki.fi/display/ONKI/">Project Wiki</a></p>

<p>The current service is based on the FinnONTO research project by the Aalto University and the University of Helsinki between 2003 and 2012. <a href="http://www.seco.tkk.fi/projects/finnonto/index.fi.php/">FinnONTO Results</a></p>

<p>If you encounter any problems or have improvement ideas, please contact the Finto team. We are also very much interested in your success stories in using Finto -<a href="../en/feedback"> please share your experiences!</a></p>      

<h4>Links</h4>
<a href="http://wiki.helsinki.fi/display/ONKI/">Project Wiki</a><br />
<a href="http://www.seco.tkk.fi/">SeCo Website</a><br />
<a href="http://www.kansalliskirjasto.fi/">The National Library of Finland</a><br />
{% endif %}
