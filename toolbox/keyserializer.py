#!/usr/bin/env python
# -*- coding: utf-8 -*-

class KeySerializer(object):
	
	@staticmethod
	def toTuple(key_):
		return tuple(key_.split("_._"))

	@staticmethod
	def toKey(tuple_):
		if not isinstance(tuple_, tuple):
			raise
		return u"%s_._%s" % tuple_
	
if __name__ == '__main__':
	s = "a_._b"
	t = ("a", "b")
	assert s, KeySerializer.toKey(t)
	assert t, KeySerializer.toTuple(KeySerializer.toKey(t))
	assert t, KeySerializer.toTuple(s)
	assert s, KeySerializer.toKey(KeySerializer.toTuple(s))
	print KeySerializer.toTuple("de-DE_._en-EN")
	print("tests passed")