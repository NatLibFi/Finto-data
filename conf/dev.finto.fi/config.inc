<?php

// configuration for easyRDF
define("VOCABULARIES_FILE", "vocabularies.ttl");

// HTTP client configuration
define("HTTP_TIMEOUT", 3); // external HTTP request timeout in seconds

// interface languages available, and the corresponding system locales
$LANGUAGES = array(
  'fi' => 'fi_FI.utf8',
  'sv' => 'sv_SE.utf8',
  'en' => 'en_GB.utf8'
);

// default SPARQL endpoint
define("DEFAULT_ENDPOINT", "http://api.dev.finto.fi/sparql");

// how many items (maximum) to retrieve in search methods by default
define("DEFAULT_SEARCH_LIMIT", 100);

// how many items (maximum) to retrieve in transitive property queries
define("DEFAULT_TRANSITIVE_LIMIT", 1000);

// a default location for Twig template rendering
define("TEMPLATE_CACHE", "/tmp/onki-light-template-cache");

// default sparql-query extension
define("DEFAULT_SPARQL_DIALECT", "JenaText");
#define("DEFAULT_SPARQL_DIALECT", "Generic");

// default email address to send the feedback
define("FEEDBACK_ADDRESS", "onki-posti@helsinki.fi");

// whether or not to log caught exceptions
define ("LOG_CAUGHT_EXCEPTIONS", FALSE);

// customize the name of the service for the templating engine.
define("SERVICE_NAME", "Finto");

// customize the service tagline for the templating engine.
define("SERVICE_TAGLINE", "Vocabularies");

// customize the service logo
define("SERVICE_LOGO", "resource/finto-pics/finto.png");

// customize the css
define("CUSTOM_CSS", "resource/css/finto.css");

