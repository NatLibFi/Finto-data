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
var valuesBlockRegExp = /(VALUES\s+\(([^)]+)\)\s+{)([^}]*?)([ \t]*})/i;

// This regular expression matches SPARQL variable names from the
// variable list of a VALUES clause.
// e.g. ["var1", "var2"], no question marks
var variableNamesRegExp = /\w+/g;

// This regular expression matches a single row of a VALUES clause,
// i.e. a set of values enclosed in parentheses. Match groups:
// 1: the content of the row (i.e. what is within the parentheses)
var valueRowRegExp = /\(\s+([^\)]*\s+)/;
// Same as above, but with the global flag, so matches several rows.
var valueRowRegExp_all = /\(\s+([^\)]*\s+)/g;

// This regular expression matches all individual values from a VALUES row: 
// either URI tokens (full URI or qname), or literals in quotation marks.
var individualValueRegExp = /(?:[^\s"]+|"[^"]*")+/g;


function getVariables(query) {
        var matches = valuesBlockRegExp.exec(query);
        var variables = matches[2].match(variableNamesRegExp);
        return variables;
}

function getDefaultValues(query) {
        var matches = valuesBlockRegExp.exec(query);
        var valueRows = matches[3].match(valueRowRegExp_all);
        var defaultValueRow = valueRows[0].match(valueRowRegExp)[1];
        var originalValues = defaultValueRow.match(individualValueRegExp);
        
        var variables = getVariables(query);
        var defaultValues = {};
        for (var i = 0; i < variables.length; ++i) {
                defaultValues[variables[i]] = originalValues[i];
        }
        return defaultValues;
}

function replaceQueryValues(query, newValues) {
        var values = getDefaultValues(query);
        $.each(newValues, function(key, value) {
                // need to determine proper quoting for the values
                if (!values.hasOwnProperty(key) || values[key][0] == '"') {
                        // a literal value - make sure it's quoted
                        if (value[0] != '"') {
                                values[key] = JSON.stringify(value);
                        } else { // already in quotes
                                values[key] = value;
                        }
                } else {
                        // a resource value, either full URI or qname
                        if (value.indexOf('http') == 0) {
                                // make sure full URIs are enclosed in angle brackets
                                values[key] = "<" + value + ">";
                        } else {
                                values[key] = value;
                        }
                }
        });
        console.log(values);

        var variables = getVariables(query);

        var vals = $.map(variables, function(varname) {
                return values[varname];
        });
        var valueString = "( " + vals.join(" ") + " )";
        console.log(valueString);
        var matches = valuesBlockRegExp.exec(query);
        var newquery = query.replace(valuesBlockRegExp, matches[1] + "\n" + valueString + "\n" + matches[4]);
        
        return newquery;
}

function modifyQueryValues() {
        var versionDelta = $("#versions option:selected").val();
        var query = yasqe.getValue();
        var newquery = replaceQueryValues(query, {'versionDelta': versionDelta});
        yasqe.setValue(newquery);
}

function changeQuery(selectQuery, updateQuery) {
	// load select query
	$.ajax({
		url: selectQuery
	}).done(function(data) {
		yasqe.setValue(data);
		modifyQueryValues(); // plug in VALUES
		yasqe.query();
	});

	// load update query
	$.ajax({
		url: updateQuery
	}).done(function(data) {
		$('#query').text(data);
		var matches = valuesBlockRegExp.exec(data);
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
        var matches = valuesBlockRegExp.exec(query);
        var vars = matches[2].match(variableNamesRegExp);
        var values = $.map(selectedRows, function(row) {
                var vals = $.map(vars, function(varname) {
                        return node_to_value(row[varname]);
                });
                return "( " + vals.join(" ") + " )";
        });
        var newquery = query.replace(valuesBlockRegExp, matches[1] + "\n" + values.join("\n") + "\n" + matches[4]);
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
	// set event handler for choosing version
	$('#versions').on("change", function() {
	        modifyQueryValues();
	        yasqe.query();
	});
}

// initialize page after DOM has loaded
$(document).ready(function() {
        loadVersions();
});
