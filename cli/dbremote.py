#!/usr/bin/python
# -*-coding: utf-8 -*-
import couchdb, threading

class DBRemote:
	_url = 'http://server.kharkiv.p-product.com:5984/'
	_server = None
	_dbName = 'run1'
	_thread = None
	listener = None
	
	@classmethod
	def server( cls ):
		if not cls._server:
			cls._server = couchdb.client.Server( url=cls._url )
		return cls._server
	
	@classmethod
	def _dbconnect( cls ):
		cls.server()
	
	@classmethod
	def databaseList( cls ):
		return [dbName for dbName in cls.server()]
	
	@classmethod
	def database( cls, dbName=None ):
		if dbName is None:
			dbName = cls._dbName
		return cls.server()[dbName]
	
	@classmethod
	def doc( cls, filterDict ):
		print '::docQuery', filterDict
		dbName = filterDict.get( 'db', cls._dbName )
		docType = filterDict.get( 'type', None )
		docId = filterDict.get( 'id', None )
		result = {}
		db = cls.database( dbName )
		print '::docQuery:DB', db
		for doc in db:
			if docId and docId == doc:
				result = dict( db[doc].viewitems() )
				break
			if docType and ( 'type' in db[doc] ) and ( db[doc]['type'] == docType ):
				result[db[doc].id] = dict( db[doc].viewitems() )
			elif not docType:
				result[db[doc].id] = dict( db[doc].viewitems() )
		if cls.listener and hasattr( cls.listener, 'docQueryCallbackHook' ):
			cls.listener.docQueryCallbackHook( result, filterDict.get( 'emit', None ) )
		if hasattr( cls, 'docQueryCallback' ):
			cls.docQueryCallback( result, filterDict.get( 'emit', None ) )
		return result
	
	@classmethod
	def queue( cls, callback, *arg, **kwarg ):
		cls._thread = threading.Thread( target=getattr( cls, callback ), args=arg )
		cls._thread.daemon = True
		cls._thread.start()
