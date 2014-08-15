#!/bin/bash

# Jouni Tuominen, 27.10.2008, 25.2.2009, 8.10.2010, 11.9.2013
# Osma Suominen 19.11.2013 - siivottu ja yksinkertaistettu

# Skripti uusien ysa-, allärs- ja musa-versioiden MARCXML->SKOS-konversioon ja
# svn:ään kommitoimiseen.
# Tarkoitettu ajettavaksi joka yö crontabiin, uusien ysa-, allärs- ja musa-versioiden 
# lataamisen jälkeen.

# Officially part of YSA-putki (TM)

ARGS=-Xmx1024m

CP_DIR='MARCXMLtoSKOSConverter:MARCXMLtoSKOSConverter/lib/*'

# Allärs
java $ARGS -cp $CP_DIR AllarsSKOSmuunnin allars.xml allars.rdf YSA-Allars-Groups.owl > allars-conversion.log

# MUSA
java $ARGS -cp $CP_DIR MUSASKOSmuunnin musa.xml musa.rdf > musa-conversion.log

# YSA
java $ARGS -cp $CP_DIR YSASKOSmuunnin ysa.xml ysa.rdf YSA-Allars-Groups.owl allars.rdf > ysa-conversion.log

