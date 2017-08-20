#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import io
import os.path

default_config = """
[Main]
length_table = kScript
#default_source_language = de-DE
default_text_length = 255
default_DefaultLanguage_renaming = de-DE

[kScript]
GO_.Text = 50
GO_.FunctionText = 30
PAR_.Text = 80
PAT_.Text = 50
APPLICATION_PROGRAM.Name = 50
CH_.Text = 50
P_BLCK.Text = 50
PSEP_.Text = 50
SEPAR.Text = 50
"""

class ConfigHandler(object):
	defaultSection = "Main"
	optionDefaultSourceLanguage = "default_source_language"
	optionDefaultTextLength = "default_text_length"
	optionDefaultDefaultLanguageRenaming = "default_DefaultLanguage_renaming"
	
	def __init__(self, configFile = None):
		self.configFile = configFile
		self.config = ConfigParser.RawConfigParser()
		if configFile is None:
			self.config.readfp(io.BytesIO(default_config))
		else:
			if os.path.exists(configFile):
				self.config.read(configFile)
			else:
				self.config.readfp(io.BytesIO(default_config))
		
	def _getAllFromSection(self, section):
		if not self.config.has_section(section):
			print "Error: section %s unknown" % section
			return
		opts = self.config.options(section)
		d = {} 
		for opt in opts:
			d[opt] = self.config.getint(section, opt)
		return d
	
	def getLengths(self):
		if not self.config.has_section(self.defaultSection):
			pass
		if not self.config.has_option(self.defaultSection, "length_table"):
			pass
		lt = self.config.get(self.defaultSection, "length_table")
		if not self.config.has_section(lt):
			pass
		return self._getAllFromSection(lt)
	
	def setOption(self, section, option, value):
		if not self.config.has_section(section):
			self.config.add_section(section)
		self.config.set(section, option, value)
		
	def getOption(self, section, option, default = None):  #, getfunc=get): #ConfigParser.RawConfigParser.get):
		if not self.config.has_section(section):
			return default
		if not self.config.has_option(section, option):
			return default
		return self.config.get(section, option)
	
	def setConfigfile(self, filename):
		self.configFile = filename

	def save(self, filename = None):
		fn = filename
		if fn is None:
			fn = self.configFile
		if fn is None:
			print "Error: Could not save config. No file given."
			return
		with open(fn, 'w') as configfile:
			self.config.write(configfile)

if __name__ == '__main__':
	config = ConfigHandler()
	#print config.getLengths()
	print config.getOption(config.defaultSection, config.optionDefaultSourceLanguage)
	