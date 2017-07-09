#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Node(object):
	def __init__(self, name, parent=None):
		if len(name) == 0:
			raise Exeption
		if parent != None:
			if not isinstance(parent, Node):
				raise Exception
			parent.addSubNode(self)
		self.tagname = name
		self.subnodes = []
		self.arguments = []
		self.text = u""
	
	def addSubNode(self, node):
		if not isinstance(node, Node):
			raise Exception
		if node == self:
			return
		self.subnodes.append(node)
	
	def addArgument(self, arg):
		self.arguments.append(arg)
		
	def addText(self, text):
		self.text = text
	
	#def __str__(self):
		
	#def __str__(self):
	#	return unicode(self).encode('utf-8')
	
	#def __unicode__(self):
		
	def getAsString(self):
		# start tag
		startTag = None
		if len(self.arguments) > 0:
			startTag = u"""<%(name)s %(args)s>""" % {"name": self.tagname, "args": u" ".join(self.arguments)}
		else:
			startTag = u"""<%(name)s>""" % {"name": self.tagname}
		
		# end tag
		endTag = u"""</%(name)s>""" % {"name": self.tagname}
		
		if len(self.subnodes) == 0:
			return u"%s%s%s" % (startTag, self.text, endTag)
		# 
		# #subs = []
		# #for sub in self.subnodes:
		# 	#print sub.getAsString()
		# 	#subs.append("".join())
		# 	#subs.append("".join([u"\t"+line for line in sub.getAsString().splitlines(True)]))
		# for sub in self.subnodes:
		# 	print sub.getAsString()
		# #print u" ".join([s.getAsString() for s in self.subnodes])
		# return u"%s%s%s" % (startTag, self.text, endTag)
		
		# content
		ret = startTag + u"\n"
		for sub in self.subnodes:
			ret = ret + u"".join([u"\t" + line + u"\n" for line in sub.getAsString().splitlines()])
		ret = ret + endTag
		# 		
#		ret = u"""%(stag)s
#	%(subs)s
#%(etag)s""" % {"stag": startTag, "etag": endTag, "subs": subs}#u" ".join([sub.getAsString() for sub in self.subnodes])}  #"subs": u"\n".join([sub.create() for sub in self.subnodes])}
		#else:
		#	ret = u"%s%s%s" % (startTag, self.text, endTag)
		return ret


if __name__ == '__main__':
	test = Node("test")
	bla = Node("bla")
	bla.addArgument("id=1")
	bla.addArgument("name=\"BLA\"")
	test.addSubNode(bla)
	moep = Node("moep", bla)
	moep.addText(u"ßüöä")
	#bla.addSubNode(moep)
	blub = Node("blub")
	blub.addText("BLUB")
	test.addSubNode(blub)
	
	print test.getAsString()