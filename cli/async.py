#!/usr/bin/python
# -*-coding: utf-8 -*-
from PyQt4 import QtCore
from random import randint
import time

from helper import QHelper
from transport import Transport
from dbs import DBConf, DBHistory
from dbremote import DBRemote

class WorkerThread( QtCore.QThread ):
	messageCallbackHandler = None
	
	def __init__( self, master ):
		QtCore.QThread.__init__( self )
		self.master = master
		Transport.listener = self
		DBRemote.listener = self
		DBRemote._dbconnect()
		self.build()
	
	def build( self ):
		self.connect( self.master, QtCore.SIGNAL( 'transportSignal' ), self.transportJob )
		self.connect( self.master, QtCore.SIGNAL( 'dbSignal' ), self.dbJob )
		self.start()
	
	def run( self ):
		while True:
			time.sleep( 0.1 )
	
	def transportJob( self, callback, *arg ):
		QHelper.log( '::ASYNC:CONNECT:TRANSPORT:' + callback, *arg )
		if hasattr( Transport, callback ):
			getattr( Transport, callback )( *arg )
	
	def dbJob( self, callback, *arg ):
		QHelper.log( '::ASYNC:CONNECT:DB:' + callback, *arg )
		DBRemote.queue( callback, *arg )
		#if hasattr( DBRemote, callback ):
		#	getattr( DBRemote, callback )( *arg )
	
	### Transport EXTENSION
	def projectList( self ):
		print '::projectList:QUERY'
		projectDict = DBRemote.doc( type='project' )
		projectList = [( k, v.get('title','') ) for k,v in projectDict.items()]
		print '::projectList', projectList
		self.master.emit( QtCore.SIGNAL( 'projectList' ), projectList )
	
	def projectData( self, project ):
		print '::projectData:QUERY'
		projectDataDict = DBRemote.doc( type='project', id=project )
		print '::projectData', projectDataDict
		self.master.emit( QtCore.SIGNAL( 'projectData' ), projectDataDict )
	
	"""
	def projectList( self ):
		self.messageCallbackHandler = self.projectListCallback
		self.sendMessage( DBConf.get( 'bot' ), 'project list' )
	
	def projectListCallback( self, sender, message ):
		QHelper.log( '::ASYNC:CALLBACK:projectList', sender, message )
		projectList = [line.split( ': ', 1) for line in message.split('\n') if len(line.split( ': ', 1))==2]
		self.master.emit( QtCore.SIGNAL( 'projectList' ), projectList )
	
	def projectData( self, project ):
		self.messageCallbackHandler = self.projectDataCallback
		self.sendMessage( DBConf.get( 'bot' ), 'project define ' + QHelper.str( project ) )
	
	def projectDataCallback( self, sender, message ):
		QHelper.log( '::ASYNC:CALLBACK:projectData', sender, message )
		message = QHelper.str( message ).split( ':', 1 )[1].strip()
		self.master.emit( QtCore.SIGNAL( 'projectData' ), message )
	"""
	
	def reportAction( self, data ):
		self.sendMessage( DBConf.get( 'bot' ), 'report %sh %sm on %s %s' % (
			QHelper.str( data.get( 'h', 0 ) ),
			QHelper.str( data.get( 'm', 0 ) ),
			QHelper.str( data.get( 'project', '' ) ),
			QHelper.str( data.get( 'summary', '' ) ),
		) )
	
	### Transport CALLBACK
	def connectSuccessCallbackHook( self ):
		QHelper.log( '::ASYNC:CALLBACK:connectSuccess' )
		self.master.emit( QtCore.SIGNAL( 'loginSuccess' ) )
	
	def connectErrorCallbackHook( self ):
		QHelper.log( '::ASYNC:CALLBACK:connectError' )
		self.master.emit( QtCore.SIGNAL( 'loginError' ), 'Bad login' )
	
	def serverErrorCallbackHook( self, e ):
		QHelper.log( '::ASYNC:CALLBACK:serverError' )
		self.master.emit( QtCore.SIGNAL( 'serverError' ), str( e ) )
	
	def sendMessageCallbackHook( self, recipient, message ):
		QHelper.log( '::ASYNC:CALLBACK:sendMessage' )
		DBHistory.set( DBConf.get( 'username' ), recipient, message )
	
	def getMessageCallbackHook( self, sender, message ):
		QHelper.log( '::ASYNC:CALLBACK:getMessage' )
		if self.messageCallbackHandler is not None:
			self.messageCallbackHandler( sender, message )
			self.messageCallbackHandler = None
			return
		elif message:
			DBHistory.set( sender, DBConf.get( 'username' ), message )
			self.master.emit( QtCore.SIGNAL( 'receiveMessage' ), sender, message )
	
	def presenceCallbackHook( self, contact, status ):
		QHelper.log( '::ASYNC:CALLBACK:presence' )
		self.master.emit( QtCore.SIGNAL( 'contactStatus' ), contact, status )
	
	
	
	### DBRemote CALLBACK
	def docQueryCallbackHook( self, result ):
		print '::DBRemote:doc:callback', result
