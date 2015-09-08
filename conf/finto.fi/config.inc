<?php

// configuration for easyRDF
define("VOCABULARIES_FILE", "vocabularies.ttl");

// HTTP client configuration
define("HTTP_TIMEOUT", 5); // external HTTP request timeout in seconds

// interface languages available, and the corresponding system locales
$LANGUAGES = array(
  'fi' => 'fi_FI.utf8',
  'sv' => 'sv_SE.utf8',
  'en' => 'en_GB.utf8'
);

// default SPARQL endpoint
define("DEFAULT_ENDPOINT", "http://api.finto.fi/sparql");

// how many items (maximum) to retrieve in search methods by default
define("DEFAULT_SEARCH_LIMIT", 100);

// how many items (maximum) to retrieve in transitive property queries
define("DEFAULT_TRANSITIVE_LIMIT", 1000);

// a default location for Twig template rendering
define("TEMPLATE_CACHE", "/tmp/finto.fi-template-cache");

// default sparql-query extension
define("DEFAULT_SPARQL_DIALECT", "JenaText");
#define("DEFAULT_SPARQL_DIALECT", "Generic");

// default email address to send the feedback
define("FEEDBACK_ADDRESS", "onki-posti@helsinki.fi");

// email address to set as the envelope sender for feedback messages
define("FEEDBACK_ENVELOPE_SENDER", "");

// whether or not to log caught exceptions
define ("LOG_CAUGHT_EXCEPTIONS", FALSE);

// service name for page titles etc.
define("SERVICE_NAME", "Finto");

// customize the service tagline for the templating engine.
define("SERVICE_TAGLINE", "Vocabularies");

// customize the service logo by pointing to your logo here. 
define("SERVICE_LOGO", "./resource/pics/logo.png");

// customize the css by adding your own stylesheet
define("CUSTOM_CSS", "resource/css/finto.css");
