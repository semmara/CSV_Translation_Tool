#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import csv
import codecs
import cStringIO
import os.path

DELIMITER = str(';')
QUOTECHAR = str('|')
QUOTING = csv.QUOTE_MINIMAL

class UTF8Recoder:
	"""
	Iterator that reads an encoded stream and reencodes the input to UTF-8
	"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)

	def __iter__(self):
		return self

	def next(self):
		return self.reader.next().encode("utf-8")

class UnicodeReader:
	"""
	A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)

	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]

	def __iter__(self):
		return self

class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		data = self.encoder.encode(data)
		self.stream.write(data)
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)
	
class CSVHandler(object):

	@staticmethod
	def read_from_csv_file(csvFilename):
		if not os.path.isfile(csvFilename):
			return []
		with open(csvFilename, "r") as f:
			reader = UnicodeReader(f, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=QUOTING)
			return [row for row in reader]

	@staticmethod
	def write_to_csv_file(csvFilename, data, lineterminator = '\n'):
		myexcel = csv.excel
		myexcel.lineterminator = lineterminator
		myexcel.delimiter = DELIMITER
		myexcel.quotechar = QUOTECHAR
		myexcel.quoting = QUOTING
		with open(csvFilename, "w") as f:
			writer = UnicodeWriter(f, dialect=myexcel)
			writer.writerows(data)

if __name__ == '__main__':
	import sys
	
	origFile = sys.argv[1]
	tmpFile = "/tmp/testfile"
	
	data = CSVHandler.read_from_csv_file(origFile)
	CSVHandler.write_to_csv_file(tmpFile, data)
	assert CSVHandler.read_from_csv_file(tmpFile) == data