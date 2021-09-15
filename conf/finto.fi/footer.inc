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

<!-- Piwik -->
<script type="text/javascript">
  var _paq = _paq || [];
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);
  (function() {
    var u=(("https:" == document.location.protocol) ? "https" : "http") + "://analytics.finto.fi/";
    _paq.push(["setTrackerUrl", u+"piwik.php"]);
    _paq.push(["setSiteId", "1"]);
    var d=document, g=d.createElement("script"), s=d.getElementsByTagName("script")[0]; g.type="text/javascript";
    g.defer=true; g.async=true; g.src=u+"piwik.js"; s.parentNode.insertBefore(g,s);
  })();
</script>
<!-- End Piwik Code -->

<!-- Browser Update -->
<script type="text/javascript">
var $buoop = {vs:{i:10,f:-4,o:-4,s:7,c:-4},c:4}; 
function $buo_f(){ 
 var e = document.createElement("script"); 
 e.src = "//browser-update.org/update.min.js"; 
 document.body.appendChild(e);
};
try {document.addEventListener("DOMContentLoaded", $buo_f,false)}
catch(e){window.attachEvent("onload", $buo_f)}
</script>
<!-- End Browser Update -->

<!-- YSO concepts with different color -->
<script type="text/javascript">

function createConceptObject(conceptUri, conceptData) {
  var newNode = { 
    text: getLabel(conceptData), 
    a_attr: getHrefForUri(conceptData.uri),
    uri: conceptUri,
    notation: conceptData.notation,
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
      a_attr: getHrefForUri(conceptData.narrower[i].uri),
      uri: conceptData.narrower[i].uri,
      notation: conceptData.narrower[i].notation,
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
      a_attr : getHrefForUri(conceptData.uri),
      uri: conceptData.uri,
      notation: conceptData.notation,
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
      a_attr : getHrefForUri(conceptObject.uri),
      uri: conceptObject.uri,
      notation: conceptObject.notation,
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

<!-- KANTO/finaf tweaks -->
<script type="text/javascript">

function finaf_tweak() {
    $(".prop-rdaa_P50094 li:not(.finaf-adjusted), .prop-rdaa_P50006 li:not(.finaf-adjusted)").each(function(index) {
        $(this).addClass("finaf-adjusted"); // prevent infinity loop
        $(this).find('> span').each(function(sIndex) {
            if (this.textContent.startsWith("Asteri ID:")) {
                var asteriSpan = $("<span id='finaf-adjusted-" + index + "s" + sIndex + "'>" + this.textContent.substr(11) + "</span>");
                $(this).text("Asteri ID: ");
                var copyObject = $("#uri-input-box + button.copy-clipboard").clone(true);
                copyObject.attr("for", "#finaf-adjusted-" + index + "s" + sIndex).css("margin-left", "4px");
                $(this).after(copyObject).after(asteriSpan);
            }
            if (this.textContent.startsWith("Y-tunnus:")) {
                var yTunnusSpan = $("<span id='finaf-adjusted-" + index + "s" + sIndex + "'>" + this.textContent.substr(10) + "</span>");
                $(this).text("Y-tunnus: ");
                var copyObject = $("#uri-input-box + button.copy-clipboard").clone(true);
                copyObject.attr("for", "#finaf-adjusted-" + index + "s" + sIndex).css("margin-left", "4px");
                $(this).after(copyObject).after(yTunnusSpan);
            }
        });
        $(this).find('a').each(function(aIndex) {
            var href = $(this).attr('href');
            if (href.startsWith('http:\/\/isni.org/isni/')) {
                $("<span>ISNI: </span>").insertBefore($(this));
                isni = href.replace('http:\/\/isni.org/isni/', '');
                isnistr = isni.substr(0, 4) + " " + isni.substr(4, 4) + " " + isni.substr(8, 4) + " " + isni.substr(12, 4);
                $(this).text(isnistr);
                $(this).attr("id", "finaf-adjusted-" + index + "a" + aIndex);
                var copyObject = $("#uri-input-box + button.copy-clipboard").clone(true);
                copyObject.attr("for", "#finaf-adjusted-" + index + "a" + aIndex).css("margin-left", "4px");
                $(this).after(copyObject);
            }
            if (href.startsWith('https:\/\/orcid.org/')) {
                $('<span class="orcid">ORCID:</span>').insertBefore($(this));
                orcid = href.replace('https:\/\/orcid.org/', '');
                $(this).text(orcid);
                $(this).attr("id", "finaf-adjusted-" + index + "a" + aIndex);
                var copyObject = $("#uri-input-box + button.copy-clipboard").clone(true);
                copyObject.attr("for", "#finaf-adjusted-" + index + "a" + aIndex).css("margin-left", "4px");
                $(this).after(copyObject);
            }
            if (href.startsWith('http:\/\/viaf.org/viaf/')) {
                $('<span>VIAF ID: </span>').insertBefore($(this));
                viaf = href.replace('http:\/\/viaf.org/viaf/', '');
                $(this).text(viaf);
                $(this).attr("id", "finaf-adjusted-" + index + "a" + aIndex);
                var copyObject = $("#uri-input-box + button.copy-clipboard").clone(true);
                copyObject.attr("for", "#finaf-adjusted-" + index + "a" + aIndex).css("margin-left", "4px");
                $(this).after(copyObject);
            }
        });
    });
}

$( document ).ready(function() {
    if (vocab === "finaf") {
        finaf_tweak(); // do immediately
        const mainContentNode = document.getElementById("maincontent");
        const observer = new MutationObserver(finaf_tweak);
        observer.observe(mainContentNode, {childList: true, subtree: true});
    }
});
</script>
