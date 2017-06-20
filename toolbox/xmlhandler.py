#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
enablePerformance = False
if enablePerformance:
	import xml.etree.cElementTree as ET
else:
	print "not using C implementation"
	import xml.etree.ElementTree as ET
from xml.dom import minidom
from ast import literal_eval as make_tuple

import json

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
	#import pdb; pdb.set_trace()
	ns = {'xliffns': 'urn:oasis:names:tc:xliff:document:1.2',
		  'xml': 'http://www.w3.org/XML/1998/namespace'}
	tree = ET.parse(filename)
	root = tree.getroot()
	
	l = root.findall('xliffns:file', ns)
	
	ret = {}
	for file_ in l:
		#print file_.attrib['original']
		translation = {}
		for body_ in file_:
			retTransUnit = {}
			translationKey = str((file_.attrib['source-language'], file_.attrib['target-language']))
			for transUnit in body_:
				#import pdb; pdb.set_trace()
				if firstN is not None:
					if firstN is 0:
						break
					if firstN > 0:
						firstN -= 1
				
				if transUnit.attrib['id'] in retTransUnit.keys():
					print "ERROR: double key found for", transUnit.attrib['id']
					continue
				
				st = {}
				src = transUnit.find('xliffns:source', ns)
				if src is not None:
					st['source'] = src.text
				else:
					print "ERROR: no source found for", transUnit.attrib['id']
					continue
				trgt = transUnit.find('xliffns:target', ns)
				if trgt is not None:
					if trgt.text is not None:
						st['target'] = trgt.text
				# 	else:
				# 		print "target.text is None:"
				# 		print "\t", translationKey
				# 		print "\t", transUnit.attrib['id']
				# 		print "\t", src.text
				# 		print "\t", trgt.text
				# 		print
				# else:
				# 	print "target is None"
				
				retTransUnit[transUnit.attrib['id']] = st
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
	
	def prettify(elem):
		rough_string = ET.tostring(elem, encoding='utf-8', method='xml')
		reparsed = minidom.parseString(rough_string)
		return reparsed.toprettyxml(indent="\t").encode('utf8')

	root = ET.Element('xliff')
	root.attrib['version'] = "1.2"
	root.attrib['xmlns'] = "urn:oasis:names:tc:xliff:document:1.2"
	for file_, fileVal in d.iteritems():
		for transLang, transVal in fileVal.iteritems():
			fileTag = ET.SubElement(root, 'file')
			fileTag.attrib['original'] = file_
			src, trgt = make_tuple(transLang)
			fileTag.attrib['source-language'] = src
			fileTag.attrib['datatype'] = 'plaintext'
			fileTag.attrib['target-language'] = trgt
			
			bodyTag = ET.SubElement(fileTag, 'body')
			
			for tuId, tuCont in transVal.iteritems():
				transUnitTag = ET.SubElement(bodyTag, 'trans-unit')
				transUnitTag.attrib['id'] = tuId
				transUnitTag.attrib['maxwidth'] = str(tuCont['len'])
				transUnitTag.attrib['size-unit'] = "char"
				
				if "source" not in tuCont:
					continue
				
				src = ET.SubElement(transUnitTag, 'source')
				src.attrib['xml:space'] = "preserve"
				src.text = tuCont['source']
				
				if "target" in tuCont:
					trgt = ET.SubElement(transUnitTag, 'target')
					trgt.attrib['xml:space'] = "preserve"
					trgt.text = tuCont['target']
	
	# modify encoding and prettify
	cont = prettify(root)
	cont = cont.replace('<target xml:space="preserve"/>', '<target xml:space="preserve"></target>')
	
	# write xml to file
	with open(filename, 'w') as f:
		f.write(cont)


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
	
