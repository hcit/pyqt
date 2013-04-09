#!/usr/bin/python
# -*-coding: utf-8 -*-
import couchdb, threading

class DBRemote:
	_url = 'http://server.kharkiv.p-product.com:5984/'
	_server = None
	_dbName = 'run1'
	_thread = None
	_task = []
	listener = None
	
	@classmethod
	def server( cls ):
		if not cls._server:
			cls._server = couchdb.client.Server( url=cls._url )
			cls._set_process()
		return cls._server
	
	@classmethod
	def databaseList( cls ):
		return [dbName for dbName in cls.server()]
	
	@classmethod
	def database( cls, dbName=None ):
		if dbName is None:
			dbName = cls._dbName
		return cls.server()[dbName]
	
	@classmethod
	def docQuery( cls, *arg, **kwarg ):
		dbName = kwarg.get( 'db', cls._dbName )
		docType = kwarg.get( 'type', None )
		docId = kwarg.get( 'id', None )
		result = {}
		db = cls.database( dbName )
		for doc in db:
			if docId and docId == doc:
				result = dict( db[doc].viewitems() )
				break
			if docType and ( 'type' in db[doc] ) and ( db[doc]['type'] == docType ):
				result[db[doc].id] = dict( db[doc].viewitems() )
			elif not docType:
				result[db[doc].id] = dict( db[doc].viewitems() )
		if cls.listener and hasattr( cls.listener, 'docQueryCallbackHook' ):
			cls.listener.docQueryCallbackHook( result )
		if hasattr( cls, 'docQueryCallback' ):
			cls.docQueryCallback( result )
		print '::DQ',result
		return result
	
	@classmethod
	def doc( cls, kwarg ):
		return cls.docQuery( **kwarg )
		#cls._task.insert( 0, ( 'docQuery', kwarg ) )
	
	@classmethod
	def _set_process( cls ):
		return
		cls._thread = threading.Thread( target=cls._process, args=( cls, ) )
		cls._thread.daemon = True
		cls._thread.start()
	
	@classmethod
	def _process( cls ):
		while True:
			try:
				cls._process_task()
			except Exception as e:
				print '::EXC'
	
	@classmethod
	def _process_task( cls ):
		print '::TASK', cls._task
		if len( cls._task ):
			callback, arg, kwarg = cls._task.pop()
			getattr( cls, callback )( *arg, **kwarg )

"""
if __name__ == '__main__':
	print DBRemote.doc( type='project', id='PPMBOT' )
	print DBRemote.doc( type='project' )
"""
