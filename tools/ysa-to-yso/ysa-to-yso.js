// initialize YASQE and YASR
var yasqe = YASQE(document.getElementById("yasqe"), {
	sparql: {
		showQueryButton: true,
		endpoint: endpoint
	},
	persistent: null,
	value: '# Valitse ensin kysely vasemmalta'
});
YASR.plugins.table.defaults.fetchTitlesFromPreflabel = false;
YASR.plugins.table.defaults.mergeLabelsWithUris = true;
YASR.plugins.table.defaults.callbacks.onCellClick = function(td, event) {
        var tr = $(td).parent();
        var rownumtd = $(tr).children()[0];
        var index = parseInt($(rownumtd).text()) - 1;
        var row = yasr.results.getBindings()[index];
        if (index in selectedRows) {
                $(tr).removeClass('selected');
                delete selectedRows[index];
        } else {
                $(tr).addClass('selected');
                selectedRows[index] = row;
        }
        console.log(selectedRows);
        refreshUpdateQuery();
        
//        console.log(event);
//        console.log(yasr.results.getVariables());
//        console.log(yasr.results.getBindings());
};

var yasr = YASR(document.getElementById("yasr"), {
	//this way, the URLs in the results are prettified using the defined prefixes in the query
	getUsedPrefixes: yasqe.getPrefixesFromQuery,
	persistency: {
		prefix: false
	}
});

 
// link YASQE and YASR together
yasqe.options.sparql.callbacks.complete = yasr.setResponse;


// store current selection of result rows
var selectedRows = {};



// This regular expression will parse a VALUES clause from a SPARQL query
// and return the following match groups:
// 0: the whole VALUES clause
// 1: opening clause e.g. "VALUES (?var1 ?var2) {"
// 2: variables e.g. "?var1 ?var2"
// 3: content of the block (everything within {})
// 4: closing "}"
var valuesRegExp = /(VALUES\s+\(([^)]+)\)\s+{)([^}]*?)([ \t]*})/i;

function changeQuery(selectQuery, updateQuery) {
	// load select query
	$.ajax({
		url: selectQuery
	}).done(function(data) {
		yasqe.setValue(data);
		yasqe.query();
	});

	// load update query
	$.ajax({
		url: updateQuery
	}).done(function(data) {
		$('#query').text(data);
		var matches = valuesRegExp.exec(data);
		console.log(matches);
		var vars = matches[2].match(/\S+/g);
		console.log(vars);
	});
}

function node_to_value(node) {
        switch(node.type) {
                case 'uri':
                        return '<' + node.value + '>';
                case 'literal':
                        if ('xml:lang' in node) {
                                return '"' + node.value + '"@' + node['xml:lang'];
                        } else if ('datatype' in node) {
                                return '"' + node.value + '"^^<' + node.datatype + ">";
                        } else {
                                return '"' + node.value + '"'
                        }
                default:
                        return 'undef'; // will be used for blank nodes - is this a problem?
        }
}

function refreshUpdateQuery() {
        var query = $('#query').text();
        var matches = valuesRegExp.exec(query);
        var vars = matches[2].match(/\w+/g);
        var values = $.map(selectedRows, function(row) {
                var vals = $.map(vars, function(varname) {
                        return node_to_value(row[varname]);
                });
                return "( " + vals.join(" ") + " )";
        });
        var newquery = query.replace(valuesRegExp, matches[1] + "\n" + values.join("\n") + "\n" + matches[4]);
        console.log(newquery);
        $('#query').text(newquery);
}

function loadVersions() {
	var versionQuery = "PREFIX sh: <http://purl.org/skos-history/>\
	PREFIX sc: <http://purl.org/science/owl/sciencecommons/>\
	PREFIX dc: <http://purl.org/dc/elements/1.1/>\
	SELECT * {\
		?sd a sh:SchemeDelta .\
		?sd sh:deltaFrom/dc:identifier ?fromId .\
		?sd sh:deltaTo/dc:identifier ?toId .\
		}";

	$.ajax({
		url: endpoint,
		data: { query: versionQuery }
	}).done(function(data) {
		$.each(data.results.bindings, function(index, row) {
			var label = row.fromId.value + " &rarr; " + row.toId.value;
			$('#versions').append($('<option>', { value: row.sd.value }).html(label));
		});
	});
}

// initialize page after DOM has loaded
$(document).ready(function() {
        loadVersions();
});
