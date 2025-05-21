<div class="right-box">

<link rel="stylesheet" type="text/css"
      href="resource/css/toots.css">

{% if request.lang == 'fi' %}
<h1>Finto Mastodonissa</h1>
{% elseif request.lang == 'sv' %}
<h1>Finto på Mastodon</h1>
{% elseif request.lang == 'en' %}
<h1>Finto on Mastodon</h1>
{% elseif request.lang == 'se' %}
<h1>Finto Mastodonis</h1>
{% endif %}

<a class="mastodon-feed"
   href="https://some.kansalliskirjasto.fi/@Finto"
   data-toot-limit="3"
   data-exclude-replies="true"
   data-exclude-reblogs="true">@Finto@some.kansalliskirjasto.fi</a>

<script type="module" src="resource/js/emfed-wrapper.mjs"></script>

</div>
