{# This is the template for the front page welcome box. You can enter any html here and show different language versions by using the lang value in a twig conditional as demonstrated below. #}
<div class="welcome-box">
{% if request.lang == 'fi' %}
<h1>Tervetuloa Finto-palveluun!</h1>
<p>Finto on suomalainen sanasto- ja ontologiapalvelu, joka mahdollistaa sanastojen julkaisun ja selailun. Palvelu tarjoaa myös <a href="http://api.finto.fi/">rajapinnat</a> sanastojen ja ontologioiden hyödyntämiseen muissa ohjelmistoissa.</p>
{% elseif request.lang == 'sv' %}
<h1>Välkommen till Finto-service!</h1>
<p>Finto är en finländsk tesaurus- och ontologiservice som erbjuder möjlighet att publicera och använda terminologier. Servicen erbjuder också <a href="http://api.finto.fi/">gränssnitt</a> för utnyttjande av ontologier i andra program.</p>
{% elseif request.lang == 'en' %}
<h1>Welcome to the Finto service!</h1>
<p>Finto is a Finnish thesaurus and ontology service, which enables both the publication and browsing of vocabularies. The service also offers <a href="http://api.finto.fi/">interfaces</a> for integrating the thesauri and ontologies into other applications and systems.</p>
{% endif %}
</div>
