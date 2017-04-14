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
	
	def read(self, cmd):
		cur = self.__connection.cursor()
		print cmd
		cur.execute(cmd)
		return cur.fetchall()
	
	def write(self, cmd):
		self.__connection.rollback()  # there shouldn't be anything
		cur = self.__connection.cursor()
		try:
			print cmd
			cur.execute(cmd)
		except sqlite3.IntegrityError:
			print "ERROR: ID already exists in PRIMARY KEY column"
		else:
			self.__connection.commit()
	
	def dump(self):
		for line in  self.__connection.iterdump():
			print line

if __name__ == '__main__':
	dbh = DBHandler(':memory:', 'test')
	dbh._DBHandler__dump()