<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" 
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns:xs="http://www.w3.org/2001/XMLSchema" 
xmlns:fn="http://www.w3.org/2005/xpath-functions" 
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" 
xmlns:skos="http://www.w3.org/2004/02/skos/core#"
xmlns:owl="http://www.w3.org/2002/07/owl#"
xmlns:dct="http://purl.org/dc/terms/"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:jhsSanasto="http://jhsmeta.fi/schemas/JHS_Metatiedot_Kasiteartikkeli_Atomaarinen_20100311.xsd" 
xmlns:jhsKasite="http://jhsmeta.fi/schemas/JHS_Metatiedot_Kasiteartikkeli_20100311.xsd" 
xmlns:jhs="http://jhsmeta.fi/skos/" 
exclude-result-prefixes="xsl xs fn jhsSanasto jhsKasite">

	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:strip-space elements="*"/>
	
	<xsl:variable name="jhsnamespace" select="'http://jhsmeta.fi/skos/'"/>
	<xsl:variable name="jhstree" select="'http://jhsmeta.fi/xml/simpletree/'"/>
	
	<xsl:template match="/">
		<rdf:RDF xml:base="http://jhsmeta.fi/skos/">
			<owl:Ontology rdf:about="">
				<owl:imports rdf:resource="http://www.w3.org/2004/02/skos/core"/>
			</owl:Ontology>
			<skos:ConceptScheme>
				<xsl:attribute name="rdf:about" select="$jhsnamespace"/>
			<dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime"><xsl:value-of  select="current-dateTime()"/></dct:modified>
			<dct:language rdf:resource="http://lexvo.org/id/iso639-3/fin"/>
			<dc:title xml:lang="fi">JHSMeta - Julkishallinnon määrittelevä sanasto</dc:title>
			<dc:description xml:lang="fi">Generoitu automaattisesti JHS sanastotyöryhmän sanastotyökalusta (http://jhsmeta.fi), jossa organisaatiot muodostavat yhteisiä ja yhteentoimivuutta tukevia sanastoja.</dc:description>
			<dc:creator xml:lang="fi">JHS sanastotyöryhmä</dc:creator>
			</skos:ConceptScheme>
			<xsl:apply-templates select="document($jhstree)/*"/>
		</rdf:RDF>
	</xsl:template>
	
	<xsl:template match="item">
		<xsl:param name="parent"/>
		<xsl:variable name="tunnus" select="@tunnus"/>
		<xsl:variable name="url" select="concat('http://jhsmeta.fi/xml/simpletree/',$tunnus)"/>
		<xsl:variable name="doc" select="document($url)"/>

		<xsl:apply-templates select="$doc/*">
			<xsl:with-param name="parent" select="$tunnus"/>
		</xsl:apply-templates>
		<xsl:apply-templates>
			<xsl:with-param name="parent" select="$parent"/>
			<xsl:with-param name="id" select="$tunnus"/>
		</xsl:apply-templates>
	</xsl:template>
	
	<xsl:template match="content/name">
		<xsl:param name="parent"/>
		<xsl:param name="id"/>
		<xsl:variable name="nimi" select="."/>
		<xsl:variable name="url2" select="concat('http://jhsmeta.fi/id/',encode-for-uri($nimi))"/>
		<xsl:variable name="doc2" select="document($url2)"/>
		<xsl:apply-templates select="$doc2/*">
			<xsl:with-param name="parent" select="$parent"/>
			<xsl:with-param name="id" select="$id"/>
			<xsl:with-param name="seeAlso" select="concat('http://jhsmeta.fi/page/',encode-for-uri($nimi))"/>
		</xsl:apply-templates>
	</xsl:template>
	
	<xsl:template match="jhsKasite:Kasiteartikkeli">
		<xsl:param name="parent"/>
		<xsl:param name="id"/>
		<xsl:param name="seeAlso"/>
		<xsl:variable name="tila" select="jhsSanasto:TilaTeksti/text()"/>
		<!--<xsl:if test="$tila='Hyväksytty' or $tila='Luonnos'"> -->
			<xsl:variable name="idURI" select="concat($jhsnamespace,$id)"/>
			<skos:Concept>
				<xsl:attribute name="rdf:about"><xsl:value-of select="$idURI"/></xsl:attribute>
				<xsl:if test="$parent">
					<xsl:variable name="parentURI" select="concat($jhsnamespace,encode-for-uri($parent))"/>
					<skos:broader>
						<xsl:attribute name="rdf:resource"><xsl:value-of select="$parentURI"/></xsl:attribute>
					</skos:broader>
				</xsl:if>
				<xsl:apply-templates/>
				<skos:inScheme>
					<xsl:attribute name="rdf:resource" select="$jhsnamespace"/>
				</skos:inScheme>
				<rdfs:seeAlso>
					<xsl:attribute name="rdf:resource" select="$seeAlso"/>
				</rdfs:seeAlso>
				<owl:versionInfo><xsl:value-of select="$tila"/></owl:versionInfo>
			</skos:Concept>
		<!--</xsl:if>-->
	</xsl:template>
	
	<xsl:template match="jhsSanasto:MaaritelmaTeksti">
		<skos:definition>
			<xsl:attribute name="xml:lang" select="@xml:lang"/>
			<xsl:value-of select="normalize-space()"/>
		</skos:definition>
	</xsl:template>
	
	<xsl:template match="jhsSanasto:SovittuTermiTeksti">
		<skos:prefLabel>
			<xsl:attribute name="xml:lang" select="@xml:lang"/>
			<xsl:value-of select="normalize-space()"/>
		</skos:prefLabel>
	</xsl:template>
	
	<xsl:template match="jhsSanasto:EsimerkkiTeksti">
		<skos:example>
		<xsl:attribute name="xml:lang" select="@xml:lang"/>
			<xsl:value-of select="normalize-space()"/>
		</skos:example>
	</xsl:template>
	
	<xsl:template match="jhsSanasto:SuhdeTeksti">
		<xsl:variable name="fullid" select="."/>
		<xsl:variable name="id" select="tokenize($fullid,'/')[last()]"/>
		<skos:related>
			<xsl:attribute name="rdf:resource"><xsl:value-of select="concat($jhsnamespace,encode-for-uri($id))"/></xsl:attribute>
		</skos:related>
	</xsl:template>
	
	<xsl:template match="text()">
	</xsl:template>
	
</xsl:stylesheet>
