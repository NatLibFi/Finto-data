<div class="right-box">

<link rel="stylesheet" type="text/css"
      href="resource/css/toots.css">

{% if request.lang == 'fi' %}
<h1>Ajankohtaista</h1>
{% elseif request.lang == 'sv' %}
<h1>Aktuellt</h1>
{% elseif request.lang == 'en' %}
<h1>News</h1>
{% elseif request.lang == 'se' %}
<h1>Ođđasat</h1>
{% endif %}

<a class="mastodon-feed"
   href="https://some.kansalliskirjasto.fi/@Finto"
   rel="me"
   data-toot-limit="3"
   data-exclude-replies="true"
   data-exclude-reblogs="true">@Finto@some.kansalliskirjasto.fi</a>

{% if request.lang == 'fi' %}
<p><a class="mastodon-follow" href="https://some.kansalliskirjasto.fi/@Finto">Seuraa Fintoa Mastodonissa</a></p>
{% elseif request.lang == 'sv' %}
<p><a class="mastodon-follow" href="https://some.kansalliskirjasto.fi/@Finto">Följ Finto på Mastodon</a></p>
{% elseif request.lang == 'en' %}
<p><a class="mastodon-follow" href="https://some.kansalliskirjasto.fi/@Finto">Follow Finto on Mastodon</a></p>
{% elseif request.lang == 'se' %}
<p><a class="mastodon-follow" href="https://some.kansalliskirjasto.fi/@Finto">Čuovvu Finto Mastodonas</a></p>
{% endif %}

<script type="module" src="resource/js/emfed-wrapper.mjs"></script>

</div>
