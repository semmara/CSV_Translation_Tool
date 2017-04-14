#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from csvmgmt.csvhandler import CSVHandler
from dbmgmt.dbcmdmanager import DBCmdManager

class Translate(object):
	def __init__(self):
		pass

if __name__ == '__main__':
	import argparse
	
	DEFAULT_INPUT_FILENAME = "input.csv"
	DEFAULT_OUTPUT_FILENAME = "output.csv"
	# 
	parser = argparse.ArgumentParser(description="translate content with help of database")
	parser.add_argument('-i', "--inputfile", help='input file', default=DEFAULT_INPUT_FILENAME)
	# parser.add_argument('-o', "--outputfile", help='output file', default=DEFAULT_OUTPUT_FILENAME)
	# parser.add_argument('-v', "--verbose", help="increase output verbosity", action="store_true")
	args = parser.parse_args()
	
	inputData = CSVHandler.read_from_csv_file(args.inputfile)
	inputHeader = inputData[0]
	inputData = inputData[1:]

	db = DBCmdManager(':memory:')
	for row in inputData:
		db.addText(inputHeader[2], str((row[0], row[1])), row[2])
		db.addText(inputHeader[3], str((row[0], row[1])), row[3])
	#db.dump()
	
	print '-' * 80
	for row in inputData:
		print db.getText(inputHeader[2], str((row[0], row[1])))
	