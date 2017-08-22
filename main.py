#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import sys

import os.path
from toolbox.dbmgmt.dbcmdmanager import DBCmdManager
from toolbox.xmlhandler import xmlToDict, dictToXml
from toolbox.confighandler import ConfigHandler
from toolbox.csvmgmt.csvhandler import CSVHandler
from toolbox.keyserializer import KeySerializer
from itertools import permutations

DEFAULT_TEXT_LEN = 255

def importXml(args, config):
	if args.verbose:
		print "command: import xml"
	if args.simulate_database:
		args.dbFile = ':memory:'
	if args.verbose:
		print args
		print "working directory:", args.C
	
	d = xmlToDict(args.inputfile)
	db = DBCmdManager(args.dbFile)
	for translation, translationValue in d.iteritems():
		srcLang, trgtLang = KeySerializer.toTuple(translation)
		if args.verbose:
			print "translation from %s to %s" % KeySerializer.toTuple(translation)
		for key, keyValue in translationValue.iteritems():
			st = db.getText(srcLang, key)
			if st is None:
				if args.verbose:
					print "Source is not in database. Adding source."
				db.addText(srcLang, key, keyValue['source'])
			# TODO: sanity check
			#elif st is not unicode(keyValue['source']):
			#	print "Error in source:", srcLang, key, repr(keyValue['source']), type(keyValue['source']), repr(st), type(st)
			#	continue
			
			if 'target' not in keyValue:
				if args.verbose:
					print "keyValue:", keyValue
					print "target not in keyValue"
				continue
			txt = db.getText(trgtLang, key)
			if txt == None:
				db.addText(trgtLang, key, keyValue['target'])
			elif txt != keyValue['target']:
				if args.force_overwrite_existing:
					print "Warning: key '%s' already existing in '%s'" % (key, trgtLang)
					try:
						print "         current content:", txt
					except:
						print "         current content: <contians non printable characters>"
					print "         new content:    ", keyValue['target']
					if raw_input('overwrite [y/N]:').lower() == 'y':
						db.deleteItem(trgtLang, key)
						db.addText(trgtLang, key, keyValue['target'])
						print "value overwritten"
					else:
						print "skipped item"
				else:
					print "Error in target:", trgtLang, key, keyValue['target'], txt

def exportXml(args, config):
	if not os.path.isfile(args.dbFile):
		print "creating database"
	if args.verbose:
		print "command: export xml"
		print args
		print "working directory:", args.C
	
	db = DBCmdManager(args.dbFile)
	d = {}
	
	srcTbl = args.sourceTranslationLanguage
	if srcTbl is None:
		print "no source language given"
		return
	trgTbl = args.targetTranslationLanguage
	missingKeys = db.getMissingKeys(srcTbl, trgTbl)  #[:15]
	
	if len(missingKeys) == 0:
		print "nothing found to translate from '%s' to '%s'" % (srcTbl, trgTbl)
		return
	
	translationKey = KeySerializer.toKey((srcTbl, trgTbl))
	
	fileOrig = translationKey  # or use sth. like: fileOrig = 'default'
	for key in missingKeys:
		# create file
		if fileOrig not in d:
			d[fileOrig] = {}
		
		# create transunit
		if translationKey not in d[fileOrig]:
			d[fileOrig][translationKey] = {}
		
		# source data
		if args.withTargetTag:
			d[fileOrig][translationKey][key] = { 'source': db.getText(srcTbl, key), 'target': '' }
		else:
			d[fileOrig][translationKey][key] = { 'source': db.getText(srcTbl, key) }
		d[fileOrig][translationKey][key]['len'] = config.getOption(config.defaultSection, config.optionDefaultTextLength, DEFAULT_TEXT_LEN)
		k1, k2 = KeySerializer.toTuple(key)
		for c1, c2 in config.getLengths().items():
			if c1.find('.') < 0:
				continue
			c1key, c1type = c1.rsplit('.', 1)
			if k1.upper().find(c1key.upper()) < 0:
				continue
			if k2.upper() != c1type.upper():
				continue
			d[fileOrig][translationKey][key]['len'] = c2
	
	# create file
	filename = args.outputfile
	dictToXml(d, filename)
	print "created", filename

def importCsv(args, config):
	if args.verbose:
		print "command: importcsv"
		print args
		print "working directory:", args.C
	
	dataColumn = 2  # source translation column
	
	# read input csv
	inputCsvData = CSVHandler.read_from_csv_file(args.inputfile)
	
	# sanity checks
	if len(inputCsvData) == 0:
		print "no data found"
		return
	if len(inputCsvData[0]) < dataColumn + 1:
		print "Number of columns to low. Needed:", dataColumn + 1
		return
	
	# import data from input csv
	dbcm = DBCmdManager(args.dbFile)
	if not args.noDatabaseImport:
		
		# get stl (source translation language)
		cfg = ConfigHandler(args.cfgFile)
		stl = cfg.getOption(cfg.defaultSection, cfg.optionDefaultDefaultLanguageRenaming)
		if stl is None:
			stl = inputCsvData[0][dataColumn]  # 'DefaultLanguage'
		
		for line in inputCsvData[1:]:  # ignore header
			key = KeySerializer.toKey(tuple(line[:2]))
			data = line[dataColumn]
			# ignore empty data
			if data in [None, '']:
				print "empty data for key", key
				continue
			needTranslation = True
			# check database for current key
			dbCont = dbcm.getText(stl, key)
			if dbCont is not None:
				if data == dbCont:
					continue
				else:
					if args.forceOverwriteExistingData:
						# overwrite database content
						dbcm.addText(stl, key, data)
					else:
						print "database value and csv value are unequal. Use 'forceOverwriteExistingData' to update database."
			else:
				# add to database
				dbcm.addText(stl, key, data)

def appendTranslationToCsv(args, config):
	if args.verbose:
		print "command: translate"
		print args
		print "working directory:", args.C
	
	# read input csv
	inputCsvData = CSVHandler.read_from_csv_file(args.inputfile)
	
	# sanity checks
	if len(inputCsvData) == 0:
		print "no data found"
		return
	if len(inputCsvData[0]) < 3:
		print "missing default language"
		return
	
	# get target translation language
	ttls = args.targetTranslationLanguage
	dbcm = DBCmdManager(args.dbFile)
	for ttl in ttls:
		if ttl not in dbcm.getExistingTablenames():
			print "#" * 80
			print "Warning: No translation table found. Please check given target language", ttl
			print "#" * 80
			if args.yes:
				ttls.discard(ttl)
			else:
				if raw_input("skip translation language '%s' [y/N]:" % ttl).lower() == 'y':
					ttls.discard(ttl)
				else:
					sys.exit(1)
	
	outputCsvData = inputCsvData[:]
	
	# remove existing translations
	#for line in outputCsvData:
	#	line = line[:3]
	
	for ttl in ttls:
		# extend header
		outputCsvData[0].append(ttl)
		
		# get translation from db (ignore empty input fields)
		for lineIdx in range(1, len(outputCsvData)):
			key = KeySerializer.toKey(tuple(outputCsvData[lineIdx][:2]))
			value = dbcm.getText(ttl, key)
			if value is None:
				print "translation value not in database", ttl, key
				outputCsvData[lineIdx].append('')
			else:
				try:
					print "append", ttl, key, value
				except:
					print "append", ttl, key
				outputCsvData[lineIdx].append(value)
	
	# remove empty
	for line in outputCsvData[:]:
		if line[2] in [None, '']:
			outputCsvData.remove(line)
	
	# write output csv
	CSVHandler.write_to_csv_file(args.outputfile, outputCsvData, args.lineterminator)
	print "translation is complete"

def rmTranslationFromCsv(args, config):
	if args.verbose:
		print "command: remove translation from csv"
		print args
		print "working directory:", args.C
	
	# read input csv
	inputCsvData = CSVHandler.read_from_csv_file(args.inputfile)
	
	header = inputCsvData[0]
	
	if args.lang not in header:
		print "Error"
		sys.exit(1)
	
	idx = header.index(args.lang)
	outputCsvData = inputCsvData[:]
	for line in outputCsvData:
		line = line.pop(idx)
	
	CSVHandler.write_to_csv_file(args.outputfile, outputCsvData, args.lineterminator)
	print "remove of translation is complete"

def status(args, config):
	if args.verbose:
		print "command: status"
		print "working directory:", args.C
	
	if not os.path.isfile(args.dbFile):
		print "no database found"
		return
	print "database file:", args.dbFile
	
	db = DBCmdManager(args.dbFile)
	tableNames = db.getExistingTablenames()
	print "existing tables:", ", ".join(tableNames)
	for table in tableNames:
		keys = db.getKeys(table)
		print table, "content size:", len(keys)
		for key in keys:
			tup = KeySerializer.toTuple(key)
			if len(tup) > 2:
				newKey = KeySerializer.toKey(tup[-2:])
				if args.deleteEvil:
					db.deleteItem(table, key)
					print "item with evil formatted key deleted:", key
				elif args.fixEvil:
					if db.exists(table, newKey):
						if db.getText(table, key) == db.getText(table, newKey):
							db.deleteItem(table, key)
							print "item with evil formatted key fixed:", key
						else:
							print "Cannot fix item with evil formatted key:", key
					else:
						txt = db.getText(table, key)
						db.deleteItem(table, key)
						db.addText(table, newKey, txt)
						print "item with evil formatted key fixed:", key
				else:
					print "item with evil formatted key found:", key

def set_rename_DefaultLanguage(args, config):
	if args.verbose:
		print "command: rename DefaultLanguage to"
		print "config file:", args.cfgFile
	cfg = ConfigHandler(args.cfgFile)
	cfg.setOption(cfg.defaultSection, cfg.optionDefaultDefaultLanguageRenaming, args.rename_as)
	cfg.save(args.cfgFile)

def xliff_diff(args, config):
	if args.verbose:
		print "command: import xml"
	if args.verbose:
		print args
		print "working directory:", args.C
	lhs = xmlToDict(args.lhs)
	rhs = xmlToDict(args.rhs)
	
	def createContList(d):
		l = []
		for translation, translationValue in d.iteritems():
			srcLang, trgtLang = KeySerializer.toTuple(translation)
			if args.verbose:
				print "translation from %s to %s" % KeySerializer.toTuple(translation)
			for key, keyValue in translationValue.iteritems():
				#print key, keyValue
				l.append(keyValue['source'])
				#return
		return l
	
	l_lhs = createContList(lhs)
	l_rhs = createContList(rhs)
	print "number of items:", len(l_lhs), len(l_rhs)
	print "number of unique items:", len(set(l_lhs)), len(set(l_rhs))
	print "lhs unique items:", list(set(l_lhs) - set(l_rhs))
	print "rhs unique items:", list(set(l_rhs) - set(l_lhs))

if __name__ == '__main__':
	import argparse
	from os.path import expanduser, join
	from os import getcwd, chdir
	import sys
	
	HOMEDIR = expanduser("~")
	CURRDIR = getcwd()
	DEFAULT_DB_FILENAME = join(HOMEDIR, ".translation.db")
	DEFAULT_CFG_FILENAME = join(HOMEDIR, ".translation.cfg")
	DEFAULT_CSV_INPUT_FILENAME = "input.csv"
	DEFAULT_CSV_OUTPUT_FILENAME = "output.csv"
	DEFAULT_XML_INPUT_FILENAME = "input.xlf"
	DEFAULT_XML_OUTPUT_FILENAME = "output.xlf"
	DEFAULT_CSV_NEWLINE = '\n'
	
	
	# config pre stuff
	cfg = ConfigHandler(DEFAULT_CFG_FILENAME)
	
	# parent parser
	parent_parser = argparse.ArgumentParser(description="translation tool")
	parent_parser.add_argument('-C', default=CURRDIR, help="set working directory")
	parent_parser.add_argument('--dbFile', default=DEFAULT_DB_FILENAME, help="path to file of database")
	parent_parser.add_argument('--cfgFile', default=DEFAULT_CFG_FILENAME, help="path to file of configuration")
	parent_parser.add_argument('-v', "--verbose", action="store_true", help="enable verbose mode")
	subparsers = parent_parser.add_subparsers(help='sub-command help')
	
	# import xml
	import_xml_parser = subparsers.add_parser('importxml', help='import xml')
	import_xml_parser.add_argument("inputfile", help='input file', default=DEFAULT_XML_INPUT_FILENAME)
	import_xml_parser.add_argument('-s', "--simulate_database", help='simulate database', action="store_true")
	import_xml_parser.add_argument("--force_overwrite_existing", action="store_true")
	import_xml_parser.add_argument("--request_overwrite_existing", action="store_true")
	import_xml_parser.set_defaults(func=importXml)
	
	# export xml
	export_xml_parser = subparsers.add_parser('exportxml', help='export xml')
	export_xml_parser.add_argument("sourceTranslationLanguage", help='the source language (database table name) to translate from')
	export_xml_parser.add_argument("targetTranslationLanguage", help='the target language (database table name) to translate to')
	export_xml_parser.add_argument('-o', "--outputfile", help='output file', default=DEFAULT_XML_OUTPUT_FILENAME)
	export_xml_parser.add_argument('-t', "--withTargetTag", help='adds empty target tag to each trans-unit', action="store_true")
	export_xml_parser.set_defaults(func=exportXml)
	
	# import csv
	import_csv_parser = subparsers.add_parser('importcsv', help='import to database from csv')
	import_csv_parser.add_argument('-d', "--noDatabaseImport", help='do not import data to database', action="store_true")
	import_csv_parser.add_argument('-f', "--forceOverwriteExistingData", help='overwrite data already in database', action="store_true")
	import_csv_parser.add_argument("inputfile", help='input file', default=DEFAULT_CSV_INPUT_FILENAME)
	import_csv_parser.set_defaults(func=importCsv)
	
	# append translation to csv
	append_to_csv_parser = subparsers.add_parser('appendtocsv', help='append translation to csv')
	append_to_csv_parser.add_argument('-l', "--lineterminator", help='set newline characters', default=DEFAULT_CSV_NEWLINE)
	append_to_csv_parser.add_argument("inputfile", help='input file', default=DEFAULT_CSV_INPUT_FILENAME)
	append_to_csv_parser.add_argument('-o', "--outputfile", help='output file', default=DEFAULT_CSV_OUTPUT_FILENAME)
	append_to_csv_parser.add_argument("targetTranslationLanguage", help='the target language (database table name) to translate to', nargs='+')
	append_to_csv_parser.add_argument("--yes", help="applies 'yes' to all interactive questions", action="store_true")
	append_to_csv_parser.set_defaults(func=appendTranslationToCsv)
	
	# remove translation from csv
	rm_from_csv_parser = subparsers.add_parser('rmfromcsv')
	rm_from_csv_parser.add_argument('-l', "--lineterminator", help='set newline characters', default=DEFAULT_CSV_NEWLINE)
	rm_from_csv_parser.add_argument('inputfile', help='input file')
	rm_from_csv_parser.add_argument('outputfile', help='output file')
	rm_from_csv_parser.add_argument('lang', help='the languages to remove from csv', nargs='+')
	rm_from_csv_parser.set_defaults(func=rmTranslationFromCsv)
	
	# status / info
	info_parser = subparsers.add_parser('status', help='status / info')
	info_parser.add_argument("--deleteEvil", help='deletes evil formatted keys from database', action="store_true")
	info_parser.add_argument("--fixEvil", help='fixes evil formatted keys from database', action="store_true")
	info_parser.set_defaults(func=status)
	
	# set
	set_parser = subparsers.add_parser('set', help='set')
	set_parser_subparsers = set_parser.add_subparsers(help='sub-command help')
	# rename DefaultLanguage to
	rename_DefaultLanguage_to = set_parser_subparsers.add_parser('rename_DefaultLanguage')
	rename_DefaultLanguage_to.add_argument("rename_as")
	rename_DefaultLanguage_to.set_defaults(func=set_rename_DefaultLanguage)
	
	# xliff diff
	xliff_diff_parser = subparsers.add_parser('xliffdiff', help='prints diff infos to given xliff files')
	xliff_diff_parser.add_argument("lhs", help='1. xliff file')
	xliff_diff_parser.add_argument("rhs", help='2. xliff file')
	xliff_diff_parser.set_defaults(func=xliff_diff)
	
	# parse arguments
	args = parent_parser.parse_args()
	
	# check for config file
	if args.cfgFile is not DEFAULT_CFG_FILENAME and os.path.exists(args.cfgFile):
		cfg = ConfigHandler(args.cfgFile)
	cfg.save()
	
	# check db file
	if os.path.isdir(args.dbFile):
		print "Error: value of dbFile is not a filename"
		sys.exit(1)
	
	# change working directory
	try:
		chdir(args.C)
		
		# run function
		args.func(args, cfg)
	finally:
		chdir(CURRDIR)
