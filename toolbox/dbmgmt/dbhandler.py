#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sqlite3

class DBHandler(object):
	__connection = None
	
	def __init__(self, dbFilename):
		self.__connection = sqlite3.connect(dbFilename)
	
	def __del__(self):
		self.__connection.close()
	
	def read(self, sql, params = None):
		cur = self._exec1(sql)
		return cur.fetchall()
	
	# def write(self, cmd):
	# 	self.__connection.rollback()  # there shouldn't be anything
	# 	cur = self.__connection.cursor()
	# 	try:
	# 		#print cmd
	# 		cur.execute(cmd)
	# 	except sqlite3.IntegrityError:
	# 		print "ERROR: ID already exists in PRIMARY KEY column"
	# 	else:
	# 		self.__connection.commit()
	def write(self, sql, params = None):
		self.__connection.rollback()  # there shouldn't be anything
		try:
			self._exec1(sql)
		except sqlite3.IntegrityError:
			print "ERROR: ID already exists in PRIMARY KEY column"
		else:
			self.__connection.commit()
	
	def _exec1(self, sql):
		"""returns the cursor"""
		cur = self.__connection.cursor()
		#print "sql:", sql
		cur.execute(sql)
		return cur
	
	def _exec2(self, sql, params):
		"""returns the cursor"""
		cur = self.__connection.cursor()
		if params is not None and not isinstance(params, tuple):
			params = tuple(params)
		print "sql:", sql
		print "params:", params
		if params is None:
			cur.execute(sql)
		else:
			cur.execute(sql, params)
		return cur
	
	def dump(self):
		for line in  self.__connection.iterdump():
			print line

if __name__ == '__main__':
	dbh = DBHandler(':memory:')
	dbh.dump()
	
	dbh = DBHandler('/tmp/moep.db')
	dbh.dump()