<!-- Cookie Consent -->
<link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.css" />
<script src="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.js"></script>

<script>

{% if request.lang == 'fi' %}
cookieMessage = "Finto.fi-sivusto käyttää evästeitä käyttäjän kieliasetusten muistamiseen sekä käytön tilastointiin. Käyttämällä Finto.fi-sivustoa hyväksyt evästeiden käytön.";
cookieDismiss = "Selvä!";
cookieLink = "Lue lisää";
cookieHref = "https://www.kiwi.fi/x/2zOOBQ";
{% elseif request.lang == 'sv' %}
cookieMessage = "Finto.fi-sidan använder cookies för att komma ihåg användares språkinställningar och för användningsstatistik. Genom att använda Finto.fi-sidan godkänner du användningen av cookies.";
cookieDismiss = "Klart!";
cookieLink = "Läs mer";
cookieHref = "https://www.kiwi.fi/x/3jOOBQ";
{% elseif request.lang == 'en' %}
cookieMessage = "Finto.fi uses cookies to store language preferences and compile usage statistics. By using finto.fi you accept the use of cookies.";
cookieDismiss = "Got it!";
cookieLink = "Learn more";
cookieHref = "https://www.kiwi.fi/x/4DOOBQ";
{% endif %}

window.addEventListener("load", function(){
window.cookieconsent.initialise({
  "palette": {
    "popup": {
      "background": "#d4edeb",
      "text": "#333333"
    },
    "button": {
      "background": "#394554",
      "text": "#ffffff"
    }
  },
  "theme": "edgeless",
  "content": {
    "message": cookieMessage,
    "dismiss": cookieDismiss,
    "link": cookieLink,
    "href": cookieHref
  }
})});
</script>
<!-- End Cookie consent -->

<script type="text/javascript">
function createConceptObject(conceptUri, conceptData) {
  var newNode = { 
    text: getLabel(conceptData), 
    a_attr: getConceptHref(conceptData),
    uri: conceptUri,
    parents: conceptData.broader,
    state: { opened: true },
    children: []
  };
  // adding a css class for separating the yso concepts from the special domain ontology concepts
  if (vocab !== 'yso' && newNode.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
    newNode.a_attr['class'] = 'yso-concept';
  // setting the flag manually if the concept is known to have narrowers, but they aren't included eg. included topconcepts
  if(conceptData.hasChildren === true) {
    newNode.children = true;
    newNode.state.opened = false;
  }
  // if we are at a concept page we want to highlight that node and mark it as to be initially opened.
  if (newNode.uri === window.uri) { newNode.li_attr = { class: 'jstree-leaf-proper' }; }
  if (conceptData.narrower) { // filtering out the ones that don't have labels 
    newNode.children = createObjectsFromChildren(conceptData, conceptUri);
  }
  
  return newNode;
}

function createObjectsFromChildren(conceptData, conceptUri) {
  var childArray = [];
  for (var i = 0; i < conceptData.narrower.length; i++) {
    var childObject = {
      text: getLabel(conceptData.narrower[i]), 
      a_attr: getConceptHref(conceptData.narrower[i]),
      uri: conceptData.narrower[i].uri,
      parents: conceptUri,
      state: { opened: true }
    };
    if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
      childObject.a_attr['class'] = 'yso-concept';
    // if the childConcept hasn't got any children the state is not needed.
    if (conceptData.narrower[i].hasChildren) {
      childObject.children = true;
      childObject.state.opened = false;
    }
    if(!childArray[childObject.uri])
      childArray.push(childObject);
    storeUri(childObject);
  }
  return childArray;
}


function vocabRoot(topConcepts) {
  var topArray = [];
  for (var i = 0; i < topConcepts.length; i++) {
    var conceptData = topConcepts[i];
    var childObject = {
      text: conceptData.label, 
      a_attr : getConceptHref(conceptData),
      uri: conceptData.uri,
      state: { opened: false } 
    };
    if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
      childObject.a_attr['class'] = 'yso-concept';
    if (conceptData.hasChildren)
      childObject.children = true;
    if (window.showNotation && conceptData.notation)
      childObject.text = '<span class="tree-notation">' + conceptData.notation + '</span> ' + childObject.text;
    setNode(childObject);
    topArray.push(childObject);
  }
  return topArray;
}

function createObjectsFromNarrowers(narrowerResponse) {
  var childArray = [];
  for (var i = 0; i < narrowerResponse.narrower.length; i++) {
    var conceptObject = narrowerResponse.narrower[i];
    var childObject = {
      text : getLabel(conceptObject), 
      a_attr : getConceptHref(conceptObject),
      uri: conceptObject.uri,
      parents: narrowerResponse.uri,
      state: { opened: false, disabled: false, selected: false }
    };
    if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
      childObject.a_attr['class'] = 'yso-concept';
    childObject.children = conceptObject.hasChildren ? true : false;
    setNode(childObject);
    childArray.push(childObject);
  }
  return childArray;
}
</script>
