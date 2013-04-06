#!/usr/bin/python
# -*-coding: utf-8 -*-
import shelve, time, os
from helper import QHelper

class DBBase:
	path = os.path.join( 'data', '' )
	
	@classmethod
	def handle( cls ):
		if not hasattr( cls, '__handle' ):
			for i in range( 10 ):
				try:
					cls.__handle = shelve.open( cls.path )
					break
				except Exception as e:
					print '::DB EXCEPTION', e
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		if hasattr( cls, '__handle' ):
			cls.__handle.sync()
			cls.__handle.close()
			delattr( cls, '__handle' )
	
	@classmethod
	def keys( cls ):
		for i in range( 10 ):
			try:
				return cls.handle().keys()
			except Exception as e:
				print '::DB EXCEPTION', e
	
	@classmethod
	def list( cls ):
		return cls.handle().items()
	
	@classmethod
	def get( cls, key, default=None ):
		return cls.handle().get( key, default )
	
	@classmethod
	def set( cls, key, value ):
		cls.handle()[key] = value
		cls.sync()



class DBConf( DBBase ):
	path = os.path.join( 'data', 'conf.db' )



class DBJob( DBBase ):
	path = os.path.join( 'data', 'job.db' )
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			del cls.handle()[ts]
			taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, ts=None, *arg, **kwarg ):
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()



class DBCron( DBBase ):
	path = os.path.join( 'data', 'cron.db' )
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			if float( ts ) < time.time():
				del cls.handle()[ts]
				cls.handle()[str( time.time() + task['period'] )] = task
				taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, period, *arg, **kwarg ):
		cls.handle()[str( time.time() )] = {
			'period':period,
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()



class DBSchedule( DBBase ):
	path = os.path.join( 'data', 'schedule.db' )
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			del cls.handle()[ts]
			taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, ts=None, *arg, **kwarg ):
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()



class DBHistory( DBBase ):
	basepath = os.path.join( 'data', 'history' )
	path = os.path.join( 'data', 'history', '' )
	
	@classmethod
	def setPath( cls, sender, recipient ):
		filename = [ sender, recipient ]
		filename.sort()
		filename = '_'.join( filename ) + '.db'
		cls.sync()
		cls.path = os.path.join( cls.basepath, filename )
	
	@classmethod
	def set( cls, sender, recipient, message, ts=None ):
		cls.setPath( sender, recipient )
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'ts':str( int( ts ) ),
			'sender':QHelper.str( sender ),
			'recipient':QHelper.str( recipient ),
			'message':QHelper.str( message )
		}
		cls.handle().sync()
	
	@classmethod
	def get( cls, user, contact ):
		cls.setPath( user, contact )
		keys = cls.keys()
		keys.sort()
		return [cls.handle()[key] for key in keys]
