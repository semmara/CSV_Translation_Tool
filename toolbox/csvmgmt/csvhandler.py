#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import csv
import codecs

DELIMITER = ';'
QUOTECHAR = '|'
QUOTING = csv.QUOTE_MINIMAL
	
class CSVHandler(object):

	@staticmethod
	def read_from_csv_file(csvFilename):
		with codecs.open(csvFilename, "r", "cp1257") as f:
			reader = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=QUOTING)
			return [row for row in reader]
	
	@staticmethod
	def write_to_csv_file(csvFilename, data):
		with open(csvFilename, "w") as f:
			writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=QUOTING)
			writer.writerows(data)

if __name__ == '__main__':
	import sys
	
	origFile = sys.argv[1]
	tmpFile = "/tmp/testfile"
	
	data = CSVHandler.read_from_csv_file(origFile)
	CSVHandler.write_to_csv_file(tmpFile, data)
	assert CSVHandler.read_from_csv_file(tmpFile) == data