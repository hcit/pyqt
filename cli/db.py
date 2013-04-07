#!/usr/bin/python
# -*-coding: utf-8 -*-
import shelve, time, os
from helper import QHelper

class DBBase:
	filepath = [ 'data' ]
	filename = ''
	fileext = ''
	
	@classmethod
	def path( cls ):
		path = os.path.join( *cls.filepath )
		path = os.path.join( path, '.'.join( [ cls.filename, cls.fileext ] ) )
		return path
	
	@classmethod
	def handle( cls ):
		if not hasattr( cls, '__handle' ):
			for i in range( 10 ):
				try:
					cls.__handle = shelve.open( cls.path() )
					break
				except Exception as e:
					print '::DB EXCEPTION', e
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		for i in range( 10 ):
			try:
				if hasattr( cls, '__handle' ):
					cls.__handle.sync()
					cls.__handle.close()
					delattr( cls, '__handle' )
				break
			except Exception as e:
				print '::DB EXCEPTION', e
	
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
	filepath = [ 'data' ]
	filename = 'conf'
	fileext = 'db'



class DBJob( DBBase ):
	filepath = [ 'data' ]
	filename = 'job'
	fileext = 'temp'
	
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
	filepath = [ 'data' ]
	filename = 'cron'
	fileext = 'temp'
	
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
	filepath = [ 'data' ]
	filename = 'schedule'
	fileext = 'temp'
	
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
	filepath = [ 'data', 'history' ]
	filename = ''
	fileext = 'history'
	
	@classmethod
	def setPath( cls, sender, recipient ):
		filename = [ sender, recipient ]
		filename.sort()
		filename = '_'.join( filename )
		cls.sync()
		cls.filename = os.path.join( filename )
	
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



class DB:
	filepath = [ 'data', 'db' ]
	filename = 'account'
	fileext = 'db'
	_conn = None
	_cur = None
	
	"""
sqlite> CREATE TABLE contact( id INT, name TEXT, contact_group_id INT );
sqlite> CREATE TABLE contact_group( id INT, name TEXT );

last_id = cls._cur.lastrowid
	"""
	
	@classmethod
	def path( cls ):
		path = os.path.join( *cls.filepath )
		path = os.path.join( path, '.'.join( [ cls.filename, cls.fileext ] ) )
		print ( cls.filename and path or ':memory:' )
		return ( cls.filename and path or ':memory:' )
	
	@classmethod
	def _connect( cls ):
		import sqlite3
		cls._conn = sqlite3.connect( cls.path() )
		cls._conn.row_factory = sqlite3.Row
		cls._cur = cls._conn.cursor()
		
	@classmethod
	def conn( cls ):
		if not cls._conn:
			cls._connect()
		return cls._conn
	
	@classmethod
	def cur( cls ):
		if not cls._cur:
			cls._connect()
		return cls._cur
	
	@classmethod
	def execute( cls, queryString, *arg ):
		print '::DB::execute', queryString, arg
		cls.cur().execute( queryString, arg )
		
		if queryString.strip().lower().startswith( 'select' ):
			# SELECT: return result
			return cls.cur().fetchall()
		else:
			# write-query: commit after execution 
			#cls.cur().commit()
			
			if queryString.strip().lower().startswith( 'insert' ):
				# INSERT: return last inserted id
				return cls.cur().lastrowid
			else:
				return cls.cur().rowcounts
