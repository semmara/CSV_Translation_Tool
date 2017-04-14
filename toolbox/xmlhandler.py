#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
enablePerformance = False
if enablePerformance:
	import xml.etree.cElementTree as ET
else:
	print "not using C implementation"
	import xml.etree.ElementTree as ET

class XliffTransUnit(object):
	def __init__(self, ident, source, target=None):
		self.ident = ident
		self.source = source
		self.target = target
	
	def toXml(self):
		xml = None
		if self.target is not None:
			xml = """<trans-unit id="%s" maxwidth="255" size-unit="char">
	<source xml:space="preserve">%s</source>
	<target xml:space="preserve">%s</target>
</trans-unit>""" % (self.ident, self.source, self.target)
		else:
			xml = """<trans-unit id="%s" maxwidth="255" size-unit="char">
	<source xml:space="preserve">%s</source>
</trans-unit>""" % (self.ident, self.source)
		return xml
	
	def __eq__(self, other):
		if not isinstance(other, XliffTransUnit):
			raise TypeError()
		return self.ident == other.ident and self.source == other.source and self.target == other.target


class XliffFile(object):
	def __init__(self, orig, sourceLang, targetLang):
		self.orig = orig
		self.sourceLang = sourceLang
		self.targetLang = targetLang
		self.content = []
		
	def toXml(self):
		cont = "\n".join([item.toXml() for item in self.content])
		if cont is not "":
			cont = "\n" + cont + "\n"
		xml = """<file original="%s" source-language="%s" datatype="plaintext" target-language="%s">
	<body>%s
	</body>
</file>""" % (self.orig, self.sourceLang, self.targetLang, cont)
		return xml
	
	def addTransUnit(tu):
		if not isinstance(tu, XliffTransUnit):
			raise TypeError()
		self.content.append(tu)


class Xliff(object):
	def __init__(self):
		self.files = None
		pass
	
	def toXml(self):
		content = ""
		xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">%s
</xliff>""" % content
		return xml
	
	# 
	# def __str__(self):
	# 	pass
	# 
	# def __repr__(self):
	# 	pass

def xmlToDict(filename):
	ns = {'xliffns': 'urn:oasis:names:tc:xliff:document:1.2',
		  'xml': 'http://www.w3.org/XML/1998/namespace'}
	tree = ET.parse(filename)
	root = tree.getroot()
	
	l = root.findall('xliffns:file', ns)
	#print "number of 'file' elements", len(l)  # only for debug
	
	retFile = {}
	for file_ in l:
		f = {}
		#print file_.tag, file_.attrib
		for body_ in file_:
			#print body_.tag, body_.attrib
			
			retTransUnit = {}
			for transUnit in body_:
				st = {}
				#print transUnit.tag, transUnit.attrib
				src = transUnit.find('xliffns:source', ns)
				if src is not None:
					#print "->", src.tag, src.attrib, src.text
					st['source'] = src.text
				else:
					print "ERROR: no source found for", transUnit.attrib['id']
					continue
				trgt = transUnit.find('xliffns:target', ns)
				if trgt is not None:
					#print "=>", trgt.tag, trgt.attrib, trgt.text
					st['target'] = trgt.text
				
				if transUnit.attrib['id'] in retTransUnit.keys():
					print "ERROR: double key found for", transUnit.attrib['id']
				retTransUnit[transUnit.attrib['id']] = st
				#print st
				
				#break  # only for debug
			#print retTransUnit
			f[str((file_.attrib['source-language'], file_.attrib['target-language']))] = retTransUnit
			break  # only for debug
		
		#print f
		retFile[file_.attrib['original']] = f
		break  # only for debug
	
	#print retFile
	return retFile

def exportXliff():
	pass


if __name__ == '__main__':
	import sys
	impDict = xmlToDict(sys.argv[1])
	
	import json
	print json.dumps(impDict, indent=4, separators=(',', ': '))
	exit(0)

if __name__ == '__main__':
	xtu1 = XliffTransUnit("de->en", "ja", "yes")
	xtu2 = XliffTransUnit("en->de", "yes", "ja")
	assert xtu1 == xtu1
	assert xtu1 != xtu2
	xf1 = XliffFile("aFilename", "de-DE", "en-EN")
	xf1.addTransUnit
	
	#pass
	
	# from lxml import etree
	# import sys
	# 
	# tree = etree.iterparse(sys.argv[1])
	# for action, elem in tree:
	# 	print "action=%s tag=%s text=%s tail=%s" % (action, elem.tag, elem.text, elem.tail)
	
	xliff = Xliff()
	print xliff.toXml()
	
	# _ = folder.invokeFactory('News Item', 'news_en')
	# news_en = folder.news_en
	# news_en.setTitle("My english title")
	# news_en.setDescription("My english description")
	# news_en.setImageCaption("My english imageCaption")
	# news_en.setText("My english text")
	# news_en.reindexObject()
	# 
	# from slc.xliff.interfaces import IXLIFFExporter
	# xliffexporter = IXLIFFExporter(news_en)
	# xliffexporter.recursive = False
	# xliffexporter.single_file = True
	# xliffexporter.html_compatibility = False
	# xliffexporter.zip = False
	# xliffexporter.source_language=news_en.Language()
	# xliffstr = xliffexporter.export()
	# 
	# from slc.xliff.BeautifulSoup import BeautifulSoup
	# soup = BeautifulSoup(xliffstr)
	# from slc.xliff.BeautifulSoup import NavigableString
	# german_title = NavigableString(u"My german Title")
	# soup.find('trans-unit', attrs={'id':'title'}).findNext('target').append( german_title )
	# german_description = NavigableString(u"My german Description")
	# soup.find('trans-unit', attrs={'id':'description'}).findNext('target').append( german_description )
	# german_text = NavigableString(u"My german Text")
	# soup.find('trans-unit', attrs={'id':'text'}).findNext('target').append( german_text )
	# german_imageCaption = NavigableString(u"My german imageCaption")
	# soup.find('trans-unit', attrs={'id':'imageCaption'}).findNext('target').append( german_imageCaption )
	# xliffstr_de = soup.prettify()
	# "My german Title" in xliffstr_de
	# 
	# xliffstr_de = xliffstr_de.replace("<target xml:lang=\"en\">", "<target xml:lang=\"de\">")
	# xliffstr_de = xliffstr_de.replace("target-language=\"\"", "target-language=\"de\"")
	# 
	# from slc.xliff.interfaces import IXLIFFImporter
	# from zope.component import getUtility
	# xliffimporter = getUtility(IXLIFFImporter)
	# from plone.namedfile.file import NamedFile
	# xliff_file = NamedFile(data=xliffstr_de, contentType="text/xml", filename=u"transl_de.xliff")
	# xliffimporter.upload(xliff_file, html_compatibility=False)
	# 
	# from plone.multilingual.interfaces import ITranslationManager
	# news_de = ITranslationManager(news_en).get_translation('de')
	# news_de.getId()
	# #'news_en-de'
	# news_de.Title()
	# #'My german Title'
	# 'My german Description' in news_de.Description()
	# #True
	# news_de.getImageCaption()
	# #'My german imageCaption'
	# news_de.getText()
	# #'<p>My german Text</p>'
	
	