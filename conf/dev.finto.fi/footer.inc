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
