#!/usr/bin/python
# -*-coding: utf-8 -*-
import shelve, time

class DBBase:
	path = ''
	
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
	path = 'conf.db'



class DBJob( DBBase ):
	path = 'job.db'
	
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
	path = 'cron.db'
	
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
	path = 'schedule.db'
	
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
