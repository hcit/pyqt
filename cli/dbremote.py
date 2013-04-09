#!/usr/bin/python
# -*-coding: utf-8 -*-
import couchdb

class DBRemote:
	_url = 'http://server.kharkiv.p-product.com:5984/'
	_server = None
	_dbName = 'run1'
	
	@classmethod
	def server( cls ):
		if not cls._server:
			cls._server = couchdb.client.Server( url=cls._url )
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
	def doc( cls, **kwarg ):
		dbName = kwarg.get( 'db', cls._dbName )
		docType = kwarg.get( 'type', None )
		docId = kwarg.get( 'id', None )
		docList = {}
		db = cls.database( dbName )
		for doc in db:
			if docId and docId == doc:
				return dict( db[doc].viewitems() )
			if docType and ( 'type' in db[doc] ) and ( db[doc]['type'] == docType ):
				docList[db[doc].id] = dict( db[doc].viewitems() )
			elif not docType:
				docList[db[doc].id] = dict( db[doc].viewitems() )
		return docList

"""
if __name__ == '__main__':
	print DBRemote.doc( type='project', id='PPMBOT' )
	print DBRemote.doc( type='project' )
"""
