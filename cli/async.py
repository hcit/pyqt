#!/usr/bin/python
# -*-coding: utf-8 -*-
from PyQt4 import QtCore
from random import randint
import time

from helper import QHelper
from transport import Transport
from dbs import DBConf, DBJob, DBCron, DBSchedule, DBHistory

class ListenerThread( QtCore.QThread ):
	def __init__( self, master ):
		#TODO: create default scheduled tasks if file not exists
		QtCore.QThread.__init__( self )
		self.master = master
		self.build()
	
	def build( self ):
		self.master.connect( self, QtCore.SIGNAL( 'listenerSignal()' ), self.respond )
		# use the listener with do method to respond:
		#  QHelper.master().emit( QtCCore.SIGNAL( 'job' ), arg1, arg2 )
		self.connect( self.master, QtCore.SIGNAL( 'jobSignal()' ), self.do )
		self.start()
	
	def run( self ):
		while True:
			for ts, task in DBCron.get():
				DBSchedule.set( ts, task['callback'], *task['arg'], **task['kwarg'] )
			time.sleep( 0.3 )
			self.emit( QtCore.SIGNAL( 'listenerSignal()' ) )
	
	def respond( self ):
		for ts, task in DBSchedule.get():
			print '::ASYNC:emit', task['callback']
			self.master.emit( QtCore.SIGNAL( task['callback'] ), *task['arg'] )
	
	def do( self, *arg ):
		print '::ASYNC:DO', arg



class ExecutionThread( QtCore.QThread ):
	messageCallbackHandler = None
	
	def __init__( self, master ):
		QtCore.QThread.__init__( self )
		self.master = master
		self.build()
	
	def build( self ):
		self.master.connect( self, QtCore.SIGNAL( 'executionSignal()' ), self.respond )
		self.start()
	
	def run( self ):
		while True:
			for ts, task in DBJob.get():
				getattr( self, task['callback'] )( *task['arg'], **task['kwarg'] )
			time.sleep( 0.4 )
			#self.emit( QtCore.SIGNAL( 'executionSignal()' ) )
	
	def connectActionTrigger( self, username, passwd ):
		#Wrap.connect( username, passwd )
		Transport.username = username
		Transport.passwd = passwd
		Transport.listener = self
		res = Transport.execute( '_connect' )
		if res:
			DBSchedule.set( 'loginSuccess', None )
		else:
			DBSchedule.set( 'loginError', None, 'Bad login' )
	
	def helloActionTrigger( self ):
		#Wrap.hello()
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'online' )
	
	def reportActionTrigger( self, **kwarg ):
		#Wrap.report( **kwarg )
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'report %sh %sm on %s %s' % (
			QHelper.str( kwarg.get( 'h', 0 ) ),
			QHelper.str( kwarg.get( 'm', 0 ) ),
			QHelper.str( kwarg.get( 'project', '' ) ),
			QHelper.str( kwarg.get( 'summary', '' ) ),
		) )
	
	def sendMessageActionTrigger( self, recipient, message ):
		#Wrap.send( recipient, message )
		DBHistory.set( DBConf.get( 'username' ), recipient, message )
		Transport.execute( 'sendMessage', QHelper.str( recipient ), QHelper.str( message ) )
	
	def projectListActionTrigger( self ):
		#Wrap.showProjectsHook()
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project list' )
		self.__class__.messageCallbackHandler = self._projectListActionTrigger
	
	@classmethod
	def _projectListActionTrigger( cls, sender, message ):
		projectList = [line.split( ': ', 1) for line in message.split('\n') if len(line.split( ': ', 1))==2]
		DBSchedule.set( 'projectList', None, projectList )
	
	def projectDataActionTrigger( self, project ):
		#Wrap.pickProjectHook( project )
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project define ' + project )
		self.__class__.messageCallbackHandler = self._projectDataActionTrigger
	
	@classmethod
	def _projectDataActionTrigger( cls, sender, message ):
		projectInfo = message
		message = QHelper.str( message ).split( ':', 1 )[1].strip()
		DBSchedule.set( 'projectData', None, message )
	
	def respond( self ):
		for ts, task in DBJob.get():
			getattr( self.master.Action, task['callback'] )( *task['arg'], **task['kwarg'] )
	
	##########################################################################
	
	@classmethod
	def messageCallbackHook( cls, sender, message ):
		if cls.messageCallbackHandler is not None:
			cls.messageCallbackHandler( sender, message )
			cls.messageCallbackHandler = None
			return
		if message:
			DBHistory.set( sender, DBConf.get( 'username' ), message )
			DBSchedule.set( 'receiveMessage', None, sender, message )
	
	@classmethod
	def presenceCallbackHook( cls, contact, status ):
		DBSchedule.set( 'contactStatus', None, contact, status )
	
	@classmethod
	def errorCallbackHook( cls, e ):
		DBSchedule.set( 'errorActionTrigger', None, str( e ) )



class RandomActionThread( QtCore.QThread ):
	randomData = {
		'project':(
			'IZI', 'ELIAS'
		),
		'contact':(
			'Ivan', 'Nick', 'Jack', 'Petr', 'Sam', 'Eugen', 'Alex', 'Bob', 'Viktor', 'Mo', 'Fred', 'Woo', 'Bradley', 'Dmitry', 'Jim', 'Lu', DBConf.get( 'bot' ), 
		),
		'status':(
			'online', 'away', 'busy', 'unavailable', 'offline'
		),
		'callback':(
			'statusActionTrigger', 'messageActionTrigger', 'reportActionTrigger'
		)
	}
	
	@classmethod
	def getRandom( cls, dataType ):
		return cls.randomData[dataType][randint( 0, len( cls.randomData[dataType] ) - 1 )]
	
	@classmethod
	def contactListAction( cls ):
		for contact in cls.randomData['contact']:
			DBSchedule.set( 'statusActionTrigger', None, contact, cls.getRandom( 'status' ) )
	
	@classmethod
	def projectListAction( cls ):
		DBSchedule.set( 'projectListActionTrigger', None, cls.randomData['project'] )
	
	@classmethod
	def projectDataAction( cls, project ):
		DBSchedule.set( 'projectDataActionTrigger', None, '{"name":"test","lead":"Someone","members":["one","two","three"]}' )
	
	@classmethod
	def statusActionTrigger( cls ):
		contact = cls.getRandom( 'contact' )
		status = cls.getRandom( 'status' )
		return ( [ contact, status ], {} )
	
	@classmethod
	def messageActionTrigger( cls ):
		contact = cls.getRandom( 'contact' )
		letters = 'abcdefghijklmnopqrstuvwxyz.,!?-     '
		message = ''.join( [letters[randint( 0, len( letters ) - 1 )] for i in range( 0, randint( 1, 100 ) )] )
		return ( [ contact, message ], {} )
	
	@classmethod
	def reportActionTrigger( cls ):
		return ( [], {} )
	
	def __init__( self ):
		QtCore.QThread.__init__( self )
		self.build()
	
	def build( self ):
		self.start()
	
	def run( self ):
		while True:
			# if random returns a "trigger" value we run a random action
			if randint( 0, 2 ) == 1:
				callback = self.getRandom( 'callback' )
				arg, kwarg  = getattr( self, callback )()
				DBSchedule.set( callback, None, *arg, **kwarg )
			time.sleep( 0.5 )
