#!/bin/sh

INFILES="mesh-metadata.ttl mesh-skos.nt finmesh.ttl swemesh.ttl altlabels.ttl"
OUTFILE=mesh-skos.ttl
SKOSIFYHOME="../../../Skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

# running sparql constructs against the .hdt
echo 'Constructing...'
echo 'prefLabels'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat 1-prefLabels.rq`" > mesh-skos.nt
echo 'altLabels'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh --stream mesh2017.hdt "`cat 2-altLabels.rq`" >> mesh-skos.nt
echo 'scopeNotes'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat 3-scopeNotes.rq`" >> mesh-skos.nt
echo 'dates'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat 4-dates.rq`" >> mesh-skos.nt
echo 'broaders'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat 5-broaders.rq`" >> mesh-skos.nt
echo 'relateds'
~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat 6-relateds.rq`" >> mesh-skos.nt

echo 'Converting URIs...'
# converting the uris
sed -i .bak -e 's|http://id.nlm.nih.gov/mesh/2017/|http://www.yso.fi/onto/mesh/|g' mesh-skos.nt

~/bin/hdt-java-package-2.0-SNAPSHOT/bin/hdtsparql.sh mesh2017.hdt "`cat exactmatches.rq`" >> mesh-skos.nt

echo 'Running skosify...'
$SKOSIFYHOME/skosify/skosify.py -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE

echo 'Done!'
