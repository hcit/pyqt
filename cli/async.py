#!/usr/bin/python
# -*-coding: utf-8 -*-
from PyQt4 import QtCore
from random import randint
import time

from wrap import Wrap
from db import DBConf, DBJob, DBCron, DBSchedule

class ListenerThread( QtCore.QThread ):
	def __init__( self, master ):
		#TODO: create default scheduled tasks if file not exists
		QtCore.QThread.__init__( self )
		self.master = master
		self.build()
	
	def build( self ):
		self.master.connect( self, QtCore.SIGNAL( 'listenerSignal()' ), self.respond )
		self.start()
	
	def run( self ):
		while True:
			for ts, task in DBCron.get():
				DBSchedule.set( ts, task['callback'], *task['arg'], **task['kwarg'] )
			time.sleep( 0.3 )
			self.emit( QtCore.SIGNAL( 'listenerSignal()' ) )
	
	def respond( self ):
		for ts, task in DBSchedule.get():
			if hasattr( self.master.Action, task['callback'] ):
				print '::ASYNC:Action', task['callback']
				getattr( self.master.Action, task['callback'] )( *task['arg'], **task['kwarg'] )
			else:
				print '::ASYNC:emit', task['callback']
				self.master.emit( QtCore.SIGNAL( task['callback'] ), *task['arg'] )#, **task['kwarg'] )



class ExecutionThread( QtCore.QThread ):
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
	
	def connectActionTrigger( self ):
		Wrap.connect()
	
	def helloActionTrigger( self ):
		Wrap.hello()
	
	def reportActionTrigger( self, **kwarg ):
		Wrap.report( **kwarg )
	
	def sendMessageActionTrigger( self, recipient, message ):
		Wrap.send( recipient, message )
	
	def projectListActionTrigger( self, **kwarg ):
		Wrap.showProjectsHook( **kwarg )
	
	def projectDataActionTrigger( self, project ):
		Wrap.pickProjectHook( project )
	
	def contactsActionTrigger( self ):
		Wrap.showContactsHook()
	
	def respond( self ):
		for ts, task in DBJob.get():
			getattr( self.master.Action, task['callback'] )( *task['arg'], **task['kwarg'] )



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
