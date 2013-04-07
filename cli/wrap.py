#!/usr/bin/python
# -*-coding: utf-8 -*-

from transport import Transport
from db import DBConf, DBSchedule, DBHistory
from helper import QHelper



class Wrap:
	messageCallbackHandler = None
	
	@classmethod
	def connect( cls, username, passwd ):
		Transport.username = username
		Transport.passwd = passwd
		Transport.listener = cls
		res = Transport.execute( '_connect' )
		if res:
			DBSchedule.set( 'loginSuccess', None )
		else:
			DBSchedule.set( 'loginError', None, 'Bad login' )
	
	@classmethod
	def hello( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'online' )
	
	@classmethod
	def report( cls, **kwarg ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'report %sh %sm on %s %s' % (
			QHelper.str( kwarg.get( 'h', 0 ) ),
			QHelper.str( kwarg.get( 'm', 0 ) ),
			QHelper.str( kwarg.get( 'project', '' ) ),
			QHelper.str( kwarg.get( 'summary', '' ) ),
		) )
	
	@classmethod
	def help( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'help' )
	
	@classmethod
	def send( cls, to, message ):
		DBHistory.set( DBConf.get( 'username' ), to, message )
		Transport.execute( 'sendMessage', QHelper.str( to ), QHelper.str( message ) )
	
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
		#TODO??????????????? cls.refreshContactList()
	
	@classmethod
	def errorCallbackHook( cls, e ):
		DBSchedule.set( 'errorActionTrigger', None, str( e ) )
	
	@classmethod
	def contacts( cls ):
		pass
	
	
	
	@classmethod
	def refreshContactList( cls ):
		contactList = Transport.execute( 'getContactList' ).items()
		for contact in contactList:
			DBSchedule.set( 'statusActionTrigger', None, contact, 'online' )
	
	@classmethod
	def refreshProjectList( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project list' )
		cls.messageCallbackHandler = cls._refreshProjectList
	
	@classmethod
	def _refreshProjectList( cls, sender, message ):
		projectList = [line.split( ': ', 1) for line in message.split('\n') if len(line.split( ': ', 1))==2]
		DBSchedule.set( 'projectList', None, projectList )
	
	@classmethod
	def _displayProjectInfo( cls, sender, message ):
		projectInfo = message
		message = QHelper.str( message ).split( ':', 1 )[1].strip()
		DBSchedule.set( 'projectData', None, message )
	
	@classmethod
	def sendMessageHook( cls, recipient, message ):
		cls.send( recipient, message )
	
	@classmethod
	def showContactsHook( cls ):
		cls.refreshContactList()
	
	@classmethod
	def showProjectsHook( cls, **kwarg ):
		cls.refreshProjectList()
	
	@classmethod
	def pickContactHook( cls, contact ):
		#TODO load history
		messages = DBHistory.get( DBConf.get( 'username' ), contact )
	
	@classmethod
	def pickProjectHook( cls, project ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project define '+project )
		cls.messageCallbackHandler = cls._displayProjectInfo
