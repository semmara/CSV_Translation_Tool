#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import os.path
from toolbox.dbmgmt.dbcmdmanager import DBCmdManager
from toolbox.xmlhandler import xmlToDict, dictToXml
from toolbox.confighandler import ConfigHandler
from toolbox.csvmgmt.csvhandler import CSVHandler
from itertools import permutations
from ast import literal_eval as make_tuple

CSV_CODING = "cp1257"
DEFAULT_CODING = "utf8"
DEFAULT_TEXT_LEN = 255

def _toTuple(key_):
	return make_tuple(key_)

def _toKey(tuple_):
	if not isinstance(tuple_, tuple):
		raise
	return str(tuple_)

def importXml(args, config):
	if args.verbose:
		print "command: import xml"
	if args.simulate_database:
		args.dbFile = ':memory:'
	if args.verbose:
		print args
		print "working directory:", args.C
	
	d = xmlToDict(args.inputfile, False, 5)
	#exit(0)
	#import json
	#print json.dumps(d, indent=4, separators=(',', ': '))
	#print
	db = DBCmdManager(args.dbFile)
	for translation, translationValue in d.iteritems():
		srcLang, trgtLang = _toTuple(translation)
		if args.verbose:
			print "translation from %s to %s" % _toTuple(translation)
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
				print "Error in target:", trgtLang, key, keyValue['target']
				continue

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
	
	translationKey = _toKey((srcTbl, trgTbl))
	
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
		k1, k2 = _toTuple(key)
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

def translate(args, config):
	if args.verbose:
		print "command: translate"
		print args
		print "working directory:", args.C
	
	needTranslation = False
	
	# read input csv
	inputCsvData = CSVHandler.read_from_csv_file(args.inputfile)
	
	# sanity checks
	if len(inputCsvData) == 0:
		print "no data found"
		return
	if len(inputCsvData[0]) < 3:
		print "missing default language"
		return
	if len(inputCsvData[0]) < 4:
		print "no source language given"
		return
	
	# import data from input csv
	dbcm = DBCmdManager(args.dbFile)
	if not args.noDatabaseImport:
		stl = inputCsvData[0][3]  # stl := source translation language
		for line in inputCsvData[1:]:
			#key = str(tuple(line[:2]))
			key = _toKey(tuple(line[:2]))
			data = line[3].decode(CSV_CODING)
			# ignore empty data
			if data in [None, '']:
				print "empty data for key", key
				continue
			needTranslation = True
			# check database for current key
			dbCont = dbcm.getText(stl, key)
			if dbCont is not None:
				if line[3] == dbCont:
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
	
	# exit if flag is set or not
	if args.noTranslation:
		if args.verbose:
			print "no translation wanted"
			sys.exit(1)
		return
	
	# get target translation language
	ttl = args.targetTranslationLanguage
	if ttl in [None, '']:
		print "no target translation language given"
		sys.exit(1)
		return
	if needTranslation:
		if ttl not in dbcm.getExistingTablenames():
			print "no translation table found. Please check given target language"
			sys.exit(1)
			return
	
	err = False
	if needTranslation:
		# get translation from db (ignore empty input fields)
		outputCsvData = inputCsvData[:1]
		outputCsvData[0][3] = ttl  # header
		numb = 0
		for line in inputCsvData[1:]:
			numb += 1
			key = _toKey(tuple(line[:2]))
			if line[3] not in [None, ''] :  # or args.forceifemptyinputdata:
				value = dbcm.getText(ttl, key)
				if value is None:
					print "translation value not in database", ttl, key
					err = True
					print "---"
					print "len line3:", len(line[3])
					print "numb:", numb
					print "value:", value
					print "ttl:", ttl
					print "key:", key
					print "line:", line
					
					import json
					print json.dumps(outputCsvData, indent=4, separators=(',', ': ')) 
					raise
					continue
				line[3] = value.encode(CSV_CODING)
			outputCsvData.append(line)
		#print outputCsvData
	else:
		outputCsvData = inputCsvData
		outputCsvData[0][3] = ttl  # header
	
	# check if translation is complete
	if err:
		print "translation is not complete"
		sys.exit(1)
		return
	
	# write output csv
	if not args.noTranslation:
		CSVHandler.write_to_csv_file(args.outputfile, outputCsvData, args.lineterminator)
	
	print "translation is complete"
	
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
		print table, "content size:", len(db.getKeys(table))

def set_default_source_language(args, config):
	if args.verbose:
		print "command: set default source language"
		print "config file:", args.cfgFile
	cfg = ConfigHandler(args.cfgFile)
	cfg.setOption(cfg.defaultSection, cfg.optionDefaultSourceLanguage, args.source_language)
	cfg.save(args.cfgFile)

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
	import_xml_parser = subparsers.add_parser('import', help='import xml')
	import_xml_parser.add_argument("inputfile", help='input file', default=DEFAULT_XML_INPUT_FILENAME)
	import_xml_parser.add_argument('-s', "--simulate_database", help='simulate database', action="store_true")
	import_xml_parser.add_argument("--force_overwrite_existing", action="store_true")
	import_xml_parser.add_argument("--request_overwrite_existing", action="store_true")
	import_xml_parser.set_defaults(func=importXml)
	
	# export xml
	export_xml_parser = subparsers.add_parser('export', help='export xml')
	if cfg.getOption(cfg.defaultSection, cfg.optionDefaultSourceLanguage) is None:
		export_xml_parser.add_argument("sourceTranslationLanguage", help='the source language (database table name) to translate from')
	else:
		export_xml_parser.add_argument('-s', "--sourceTranslationLanguage", help='the source language (database table name) to translate from', default=cfg.getOption(cfg.defaultSection, cfg.optionDefaultSourceLanguage))
	export_xml_parser.add_argument("targetTranslationLanguage", help='the target language (database table name) to translate to')
	export_xml_parser.add_argument('-o', "--outputfile", help='output file', default=DEFAULT_XML_OUTPUT_FILENAME)
	export_xml_parser.add_argument('-t', "--withTargetTag", help='adds empty target tag to each trans-unit', action="store_true")
	export_xml_parser.set_defaults(func=exportXml)
	
	# translate csv
	translate_parser = subparsers.add_parser('translate', help='translate csv')
	translate_parser.add_argument('-i', "--inputfile", required=True, help='input file', default=DEFAULT_CSV_INPUT_FILENAME)
	translate_parser.add_argument('-o', "--outputfile", help='output file', default=DEFAULT_CSV_OUTPUT_FILENAME)
	translate_parser.add_argument('-n', "--noTranslation", help='do not write translation output file', action="store_true")
	translate_parser.add_argument('-t', "--targetTranslationLanguage", help='the target language (database table name) to translate to')
	translate_parser.add_argument('-d', "--noDatabaseImport", help='do not import data to database', action="store_true")
	translate_parser.add_argument('-f', "--forceOverwriteExistingData", help='overwrite data already in database', action="store_true")
	translate_parser.add_argument('-l', "--lineterminator", help='set newline characters', default=DEFAULT_CSV_NEWLINE)
	translate_parser.add_argument('-e', "--forceifemptyinputdata", help='check database for translation, also if data from inputfile is empty', action="store_true")
	translate_parser.set_defaults(func=translate)
	
	# status / info
	info_parser = subparsers.add_parser('status', help='status / info')
	info_parser.set_defaults(func=status)
	
	# set
	set_parser = subparsers.add_parser('set', help='set')
	set_parser_subparsers = set_parser.add_subparsers(help='sub-command help')
	# subset default
	default_parser = set_parser_subparsers.add_parser('default', help='default')
	set_default_parser_subparsers = default_parser.add_subparsers(help='sub-command help')
	# subsubset default source language
	default_source_language_parser = set_default_parser_subparsers.add_parser('source_language', help='source language')
	default_source_language_parser.add_argument("source_language", help="set default source language")
	default_source_language_parser.add_argument('-i', "--ignore_warnings", help="ignore warnings")
	default_source_language_parser.set_defaults(func=set_default_source_language)
	
	# parse arguments
	args = parent_parser.parse_args()
	
	# check for config file
	if args.cfgFile is not DEFAULT_CFG_FILENAME and os.path.exists(args.cfgFile):
		cfg = ConfigHandler(args.cfgFile)
	cfg.save()
	
	#conf = {}
	#conf["lenlimits"] = cfg.getLengths()
	
	# change working directory
	try:
		chdir(args.C)
		
		# run function
		args.func(args, cfg)
	finally:
		chdir(CURRDIR)
