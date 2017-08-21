#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
enablePerformance = False
if enablePerformance:
	import xml.etree.cElementTree as ET
else:
	print "not using C implementation"
	import xml.etree.ElementTree as ET
from .keyserializer import KeySerializer

import json
from .node import Node

def dictDepth(d):
	depth=0
	q = [(i, depth+1) for i in d.values() if isinstance(i, dict)]
	max_depth = 0
	while (q):
		n, depth = q.pop()
		max_depth = max(max_depth, depth)
		q = q + [(i, depth+1) for i in n.values() if isinstance(i, dict)]
	return max_depth

def xmlToDict(filename, respectFile = False, firstN = None):
	ns = {'xliffns': 'urn:oasis:names:tc:xliff:document:1.2',
		  'xml': 'http://www.w3.org/XML/1998/namespace'}
	tree = ET.parse(filename)
	root = tree.getroot()
	
	l = root.findall('xliffns:file', ns)
	
	ret = {}
	for file_ in l:
		translation = {}
		for body_ in file_:
			retTransUnit = {}
			translationKey = KeySerializer.toKey((file_.attrib['source-language'], file_.attrib['target-language']))
			for transUnit in body_:
				if firstN is not None:
					if firstN is 0:
						break
					if firstN > 0:
						firstN -= 1
				
				# workaround/manipulation for translation office
				transUnit_attrib_id = KeySerializer.toKey(KeySerializer.toTuple(transUnit.attrib['id'])[-2:])
				# end of workaround
				
				if transUnit_attrib_id in retTransUnit.keys():
					print "ERROR: double key found for", transUnit_attrib_id
					continue
				
				st = {}
				src = transUnit.find('xliffns:source', ns)
				if src is not None:
					st['source'] = src.text
				else:
					print "ERROR: no source found for", transUnit_attrib_id
					continue
				trgt = transUnit.find('xliffns:target', ns)
				if trgt is not None:
					if trgt.text is not None:
						st['target'] = trgt.text.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
				# 	else:
				# 		print "target.text is None:"
				# 		print "\t", translationKey
				# 		print "\t", transUnit.attrib['id']
				# 		print "\t", src.text
				# 		print "\t", trgt.text
				# 		print
				# else:
				# 	print "target is None"
				
				retTransUnit[transUnit_attrib_id] = st
				#print "+", retTransUnit
			
			if respectFile:
				translation[translationKey] = retTransUnit
			else:
				if translationKey not in ret:
					ret[translationKey] = {}
				ret[translationKey].update(retTransUnit)
				#print "++", json.dumps(ret, indent=4, separators=(',', ': '))
			
			if firstN is 0:
				break
		
		if respectFile:
			ret[file_.attrib['original']] = translation
		
		if firstN is 0:
			break
	
	return ret

def dictToXml(d, filename):
	depth = dictDepth(d)
	if depth is not 3:
		print "depth is not 3"
		return
	
	root = Node(u"xliff")
	root.addArgument(u'''version="1.2"''')
	root.addArgument(u'''xmlns="urn:oasis:names:tc:xliff:document:1.2"''')
	for file_, fileVal in d.iteritems():
		for transLang, transVal in fileVal.iteritems():
			fileTag = Node(u"file", root)
			fileTag.addArgument(u'''original="%s"''' % file_)
			src, trgt = KeySerializer.toTuple(transLang)
			fileTag.addArgument(u'''source-language="%s"''' % src)
			fileTag.addArgument(u'''datatype="plaintext"''')
			fileTag.addArgument(u'''target-language="%s"''' % trgt)
			
			bodyTag = Node(u"body", fileTag)
			
			for tuId, tuCont in transVal.iteritems():
				transUnitTag = Node(u"trans-unit", bodyTag)
				
				# workaround/manipulation for translation office
				if tuId.startswith(u"PAR_"):
					tuId = u"Parameter_._" + tuId
				elif tuId.startswith(u"PAT_"):
					tuId = u"ParameterTypeRestrictionEnumeration_._" + tuId
				elif tuId.startswith(u"ENUM_PAT_"):
					tuId = u"ParameterTypeRestrictionEnumeration_._" + tuId
				elif tuId.startswith(u"ENUM_"):
					tuId = u"ParameterTypeRestrictionEnumeration_._" + tuId
				# end of workaround
				
				transUnitTag.addArgument(u'id="%s"' % tuId)
				transUnitTag.addArgument(u'maxwidth="%s"' % str(tuCont['len']))
				transUnitTag.addArgument(u'size-unit="%s"' % "char")
				
				if "source" not in tuCont:
					continue
				
				src = Node(u"source", transUnitTag)
				src.addArgument(u'xml:space="preserve"')
				src.addText(tuCont['source'])
				
				if "target" in tuCont:
					trgt = Node(u"target", transUnitTag)
					trgt.addArgument(u'xml:space="preserve"')
					trgt.addText(tuCont['target'])
	cont = u'<?xml version="1.0" ?>\n' + root.getAsString()
	
	# sanity check
	if (cont is None) or (len(cont) == 0):
		raise Exception
	
	# write xml to file
	with open(filename, 'w') as f:
		f.write(cont.encode("utf-8"))
	return


if __name__ == '__main__':
	import sys
	import json
	
	impDictFile = xmlToDict(sys.argv[1], True)
	# impDictNoFile = xmlToDict(sys.argv[1], False)
	
	#print json.dumps(impDictFile, indent=4, separators=(',', ': '))
	# print json.dumps(impDictNoFile, indent=4, separators=(',', ': '))
	
	tmpFile = "/tmp/test.xml"
	dictToXml(impDictFile, tmpFile)
	testDict = xmlToDict(tmpFile, True)
	assert impDictFile == testDict
	print "xml parsing results are equal"
	# dictToXml(impDictNoFile, "/tmp/NF.xml")
	
	print "impDictFile:"
	print json.dumps(impDictFile, indent=4, separators=(',', ': '))
	print
	print "testDict:"
	print json.dumps(testDict, indent=4, separators=(',', ': '))
	
