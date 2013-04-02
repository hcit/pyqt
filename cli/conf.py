#!/usr/bin/python
# -*-coding: utf-8 -*-
import shelve

class Conf:
	__handle = None
	__file = 'conf.db'
	
	@classmethod
	def __get_handle( cls ):
		if not cls.__handle:
			cls.__handle = shelve.open( cls.__file )
		return cls.__handle
	
	@classmethod
	def listConf( cls ):
		return cls.__get_handle().items()
	
	@classmethod
	def getConf( cls, property, default=None ):
		return cls.__get_handle().get( property, default )
	
	@classmethod
	def setConf( cls, property, value ):
		cls.__get_handle()[property] = value
		cls.__get_handle().sync()
