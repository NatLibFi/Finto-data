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
var $buoop = {reminder: 24, l:'{{ lang }}'}; 
$buoop.ol = window.onload;
window.onload=function(){ 
 try {if ($buoop.ol) $buoop.ol();}catch (e) {}
 var e = document.createElement("script");    
 e.setAttribute("type", "text/javascript");
 e.setAttribute("src", "//browser-update.org/update.js");
 document.body.appendChild(e); 
} 
</script>
<!-- End Browser Update -->

<!-- YSO concepts with different color -->
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
