{# This is the template for the front page welcome box. You can enter any html here and show different language versions by using the lang value in a twig conditional as demonstrated below. #}
<div class="welcome-box">
{% if request.lang == 'fi' %}

<h1>Tervetuloa Finto.fi:hin!</h1>

<p>Finto.fi on keskitetty palvelu eri alojen yhteentoimiville sanastoille,
ontologioille ja luokituksille. Voit hyödyntää Finto.fi:tä sanastojen
selailuun tai integroida Finton sanastot omaan järjestelmääsi <a
href="https://api.finto.fi">avoimien rajapintojen</a> avulla.</p>

<p><a href="https://ai.finto.fi">Finto AI</a>:sta löydät myös
käyttöliittymän ja rajapinnat automaattiseen sisällönkuvailuun.</p>

{% elseif request.lang == 'sv' %}

<h1>Välkommen till Finto.fi!</h1>

<p>Finto.fi är en centraliserad service för samverkansfrämjande tesaurer,
ontologier och klassifikationer inom olika områden. Du kan utnyttja Finto.fi
för bläddring i vokabulärer eller integrera vokabulärerna i Finto med ditt
eget system genom <a href="https://api.finto.fi">öppna gränssnitt</a>.</p>

<p>På <a href="https://ai.finto.fi">Finto AI</a> hittar du också ett
användargränssnitt och ett API för automatisk innehållsbeskrivning.</p>

{% elseif request.lang == 'en' %}

<h1>Welcome to Finto.fi!</h1>

<p>Finto.fi is a centralized service for interoperable thesauri, ontologies and
classification schemes for different subject areas. You can use Finto.fi to
browse vocabularies or integrate the vocabularies into your own system using
the <a href="https://api.finto.fi">open APIs</a>.</p>

<p><a href="https://ai.finto.fi">Finto AI</a> provides a user interface and
API for automated subject indexing.</p>
  
{% elseif request.lang == 'se' %} 

<h1>Buresboahtin Finto.fi:i!</h1> 

<p>Finto.fi lea guovdilaston bálvalus sierra surggiid ovttasdoaibmi sátnerájuide, 
ontologiijaide ja klassifikašuvnnaide. Sáhtát geavahit Finto.fi-siiddu sátnerájuid 
bláđemii dahje integreret Finto sátnerájuid iežat vuogádahkii <a href="https://api.finto.fi">rabas rádjeolggožiid</a> bokte.</p> 

<p><a href="https://ai.finto.fi">Finto AI</a>:s gávnnat maiddái geavahanlavtta ja 
rádjeolggožiid automáhtalaš sisdoalu govvideapmái.</p> 

{% endif %}
</div>
