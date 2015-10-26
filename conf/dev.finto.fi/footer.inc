<script type="text/javascript">
function createConceptObject(conceptUri, conceptData) {
  var prefLabel = conceptData.prefLabel; // the json narrower response has a different structure.
  newNode = { 
    text: prefLabel, 
    a_attr: { "href" : vocab + '/' + lang + '/page/?uri=' + encodeURIComponent(conceptUri) },
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
  // if we are at a top concepts page we want to highlight that node and mark it as to be initially opened.
  if (newNode.uri === $('.uri-input-box').html()) { newNode.li_attr = { class: 'jstree-leaf-proper' }; }
  if (conceptData.notation)
    newNode.text = '<span class="tree-notation">' + conceptData.notation + '</span> ' + newNode.text;
  if (conceptData.narrower) { // filtering out the ones that don't have labels 
    var childArray = [];
    for (var child in conceptData.narrower) {
      var conceptObject = conceptData.narrower[child];
      var hasChildren = conceptObject.hasChildren; 
      var childObject = {
        text: conceptObject.label, 
        a_attr: { "href" : vocab + '/' + lang + '/page/?uri=' + encodeURIComponent(conceptData.narrower[child].uri) },
        uri: conceptData.narrower[child].uri,
        parents: conceptUri,
        state: { opened: true }
      };
      if (conceptData.narrower[child].notation)
        childObject.text = '<span class="tree-notation">' + conceptData.narrower[child].notation + '</span> ' + childObject.text;
      // adding a css class for separating the yso concepts from the special domain ontology concepts
      if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
        childObject.a_attr['class'] = 'yso-concept';
      if (child === $('.uri-input-box').html()) { /* childObject.data.attr.id = 'jstree-leaf-proper'; */ }
      // if the childConcept hasn't got any children the state is not needed.
      if (hasChildren) {
        childObject.children = true;
        childObject.state.opened = false;
      }
      if(!childArray[childObject.uri])
        childArray.push(childObject);
      storeUri(childObject);
    }
    newNode.children = childArray;
  }
  
  return newNode;
}

function vocabRoot(topConcepts) {
  var topArray = [];
  for (var i = 0; i < topConcepts.length; i++) {
    var conceptData = topConcepts[i];
    var childObject = {
      text: conceptData.label, 
      a_attr : { "href" : vocab + '/' + lang + '/page/?uri=' + encodeURIComponent(conceptData.uri) },
      uri: conceptData.uri,
      children: [],
      state: { opened: false } 
    };
    // adding a css class for separating the yso concepts from the special domain ontology concepts
    if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
      childObject.a_attr['class'] = 'yso-concept';
    if (conceptData.hasChildren)
      childObject.children = true;
    setNode(childObject);
    topArray.push(childObject);
  }
  return topArray;
}

function createObjectsFromNarrowers(narrowerResponse) {
  var childArray = [];
  for (var child in narrowerResponse.narrower) {
    var conceptObject = narrowerResponse.narrower[child];
    var hasChildren = conceptObject.hasChildren; 
    var childObject = {
      text : conceptObject.prefLabel, 
      a_attr : { "href" : vocab + '/' + lang + '/page/?uri=' + encodeURIComponent(conceptObject.uri) },
      uri: conceptObject.uri,
      parents: narrowerResponse.uri,
      state: { opened: false, disabled: false, selected: false }
    };
    // adding a css class for separating the yso concepts from the special domain ontology concepts
    if (vocab !== 'yso' && childObject.uri.indexOf('www.yso.fi/onto/yso/') !== -1)
      childObject.a_attr['class'] = 'yso-concept';
    if (conceptObject.notation)
      childObject.text = '<span class="tree-notation">' + conceptObject.notation + '</span> ' + childObject.text;
    if (hasChildren) {
      childObject.children = true;
      childObject.state.opened = false;
    }
    setNode(childObject);
    childArray.push(childObject);
  }
  return childArray;
}
</script>
