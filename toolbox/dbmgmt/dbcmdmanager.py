#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dbhandler import DBHandler

def dbf(s):
	return s.replace("'", "''")

class DBCmdManager(object):
	_checkedTablenames = []
	_dbHandler = None
	
	def __init__(self, dbFilename):
		self._dbHandler = DBHandler(dbFilename)
	
	def _createTable(self, tablename):
		if tablename in self._checkedTablenames:
			return
		self._checkedTablenames.append(tablename)
		cmd = "CREATE TABLE IF NOT EXISTS '%s' (ID TEXT PRIMARY KEY NOT NULL, TXT TEXT NOT NULL)" % tablename
		self._dbHandler.write(cmd)
	
	def addText(self, tablename, key, text):
		self._createTable(tablename)
		
		#cmd = """INSERT INTO ? (ID, TXT) VALUES (?,?)"""
		#self._dbHandler.write(cmd, [tablename, key, text])
		
		# d = {'table': dbf(tablename),
		# 	 'key': dbf(key),
		# 	 'text': dbf(text).decode('latin-1')}
		# cmd = """INSERT INTO '%(table)s' (ID, TXT) VALUES ('%(key)s', '%(text)s')""" % d
		# self._dbHandler.write(cmd)
		cmd = """INSERT INTO '%s' (ID, TXT) VALUES ('%s', '%s')""" % (dbf(tablename), dbf(key), dbf(text))
		self._dbHandler.write(cmd)
		#self._dbHandler.write(cmd, [dbf(key), dbf(text)])
		#self._dbHandler.write(cmd, [dbf(key), dbf(text).decode('latin-1')])
	
	def getText(self, tablename, key):
		if tablename not in self.getExistingTablenames():
			return None
		
		cmd = "SELECT TXT FROM '%s' WHERE ID = '%s'" % (dbf(tablename), dbf(key))
		elems = self._dbHandler.read(cmd)
		#cmd = "SELECT TXT FROM ? WHERE ID=?" # % (dbf(tablename), dbf(key))
		#elems = self._dbHandler.read(cmd, [tablename, key])
		#print "elems:", elems
		if len(elems) == 0:
			return None
		elif len(elems) == 1:
			return elems[0][0]
		else:
			return [item[0] for item in self._dbHandler.read(cmd)]
		
	def getKeys(self, tablename):
		"""Returns ID-list of table 'tablename'
		"""
		cmd = "SELECT ID FROM '%s'" % tablename
		return [item[0] for item in self._dbHandler.read(cmd)]
	
	def getMissingKeys(self, tablename1, tablename2):
		"""Returns missing IDs in table 'tablename2' compared to table 'tablename1'
		"""
		if tablename1 is tablename2:
			return []
		if tablename1 not in self.getExistingTablenames():
			return []
		if tablename2 not in self.getExistingTablenames():
			return self.getKeys(tablename1)
		keys1 = self.getKeys(tablename1)
		for item in self.getKeys(tablename2):
			if item in keys1:
				keys1.remove(item)
		return keys1
	
	def getExistingTablenames(self):
		cmd = "SELECT name FROM sqlite_master WHERE type='table'"
		return [item[0] for item in self._dbHandler.read(cmd)]
	
	def exists(self, tablename, key = None, text = None):
		if text is not None:
			return text == self.getText(tablename, key)
		if key is not None:
			return key in self.getKeys(tablename)
		return tablename in self.getExistingTablenames()
	
	def dump(self):
		self._dbHandler.dump()

if __name__ == '__main__':
	import sys, traceback
	try:
		dbcm = DBCmdManager(':memory:')
		dbcm.addText("de", "bla", "blub")
		dbcm.addText("en", "bla", "moep")
		dbcm.addText("en", "bla2", "moep2")
		dbcm.addText("de", "Spezial", u"äöüß")
		assert dbcm.getText("de", "bla") == "blub"
		assert dbcm.getText("en", "bla") == "moep"
		assert dbcm.getText("de", "Spezial") == "äöüß"
		assert dbcm.getText("de", "Spezial") == u"äöüß"
		assert dbcm.getText("en", "uiii") == None
		assert dbcm.getText("fr", "bla") == None
		assert dbcm.getKeys("en") == ['bla', 'bla2']
		assert dbcm.getMissingKeys("en", "de") == ['bla2']
		assert dbcm.getMissingKeys("de", "en") == ['Spezial']
		assert dbcm.getExistingTablenames() == ['de', 'en']
		assert dbcm.exists("de", "bla", "blub") == True
		assert dbcm.exists("de", "bla", "blub ") == False
		assert dbcm.exists("de", "bla", "asfd") == False
		assert dbcm.exists("de", "bla3", "blub") == False
		assert dbcm.exists("fr", "bla", "blub") == False
		assert dbcm.exists("de", "bla") == True
		assert dbcm.exists("de", "bla2") == False
		assert dbcm.exists("en") == True
		assert dbcm.exists("fr") == False
		
		# use case 1
		# check if in db and if equal
		assert dbcm.exists("de", "bla", "blub") == True
		# check if translation exists
		assert dbcm.exists("en", "bla") == True
		# get translation
		assert dbcm.getText("en", "bla") == "moep"
	except AssertionError as err:
		print "===", "DB START", "=" * 67
		dbcm.dump()
		print "===", "DB END", "=" * 69
		_, _, tb = sys.exc_info()
		traceback.print_tb(tb)
		tb_info = traceback.extract_tb(tb)
		filename, line, func, text = tb_info[-1]
		print 'An error occurred on line {} in statement {}'.format(line, text)
		#print 'An error occurred on line %s in statement %s' % (line, text)
		exit(1)
	else:
		print "all tests passed"