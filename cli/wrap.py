#!/usr/bin/python
# -*-coding: utf-8 -*-

import shelve, time, sys
from transport import Transport
from db import DBConf, DBSchedule
from unidecode import unidecode

def _str( string ):
	#print '::str', type( string )
	#print string
	if hasattr( string, 'toUtf8' ):
		string = str( string.toUtf8() ).decode( 'utf-8' )
	elif type( string ) == type( u' ' ):
		string = unidecode( string )
	elif not type( string ) == str:
		string = str( string )
	else:
		string = str( string )
	return string

class Wrap:
	trigger = {}
	_dbs = {}
	messageCallbackHandler = None
	
	@classmethod
	def history( cls, sender, recipient, message ):
		if sender == DBConf.get( 'username' ):
			name = recipient
		else:
			name = sender
		filename = 'history/' + DBConf.get( 'username' ) + '_' + name + '.db'
		if not filename in cls._dbs.keys():
			cls._dbs[filename] = shelve.open( filename )
		cls._dbs[filename][str( time.time() )] = {'ts':str( int( time.time() ) ),'sender':_str(sender),'recipient':_str(recipient),'message':_str(message)}
		cls._dbs[filename].sync()
	
	@classmethod
	def getHistory( cls, contact ):
		filename = 'history/' + DBConf.get( 'username' ) + '_' + contact + '.db'
		if not filename in cls._dbs.keys():
			cls._dbs[filename] = shelve.open( filename )
		keys = cls._dbs[filename].keys()
		keys.sort()
		return [cls._dbs[filename][key] for key in keys]
	
	@classmethod
	def connect( cls ):
		Transport.listener = cls
		res = Transport.execute( '_connect' )
		#res = Transport._connect()
		if res:
			DBSchedule.set( 'successActionTrigger', None )
		else:
			DBSchedule.set( 'errorActionTrigger', None, 'Bad login' )
	
	@classmethod
	def hello( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'online' )
		#Transport.sendMessage( DBConf.get( 'bot' ), 'online' )
	
	@classmethod
	def report( cls, **kwarg ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'report %sh %sm on %s %s' % (
			_str( kwarg.get( 'h', 0 ) ),
			_str( kwarg.get( 'm', 0 ) ),
			_str( kwarg.get( 'project', '' ) ),
			_str( kwarg.get( 'summary', '' ) ),
		) )
		"""
		Transport.sendMessage( DBConf.get( 'bot' ), 'report %sh %sm on %s %s' % (
			_str( kwarg.get( 'h', 0 ) ),
			_str( kwarg.get( 'm', 0 ) ),
			_str( kwarg.get( 'project', '' ) ),
			_str( kwarg.get( 'summary', '' ) ),
		) )
		"""
	
	@classmethod
	def help( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'help' )
		#Transport.sendMessage( DBConf.get( 'bot' ), 'help' )
	
	@classmethod
	def send( cls, to, message ):
		cls.history( DBConf.get( 'username' ), to, message )
		Transport.execute( 'sendMessage', _str( to ), _str( message ) )
		#Transport.sendMessage( _str( to ), _str( message ) )
	
	@classmethod
	def messageCallbackHook( cls, sender, message ):
		#if not sender in Transport.getContactList().keys():
		#	sender = DBConf.get( 'bot' )
		if cls.messageCallbackHandler is not None:
			cls.messageCallbackHandler( sender, message )
			cls.messageCallbackHandler = None
			return
		if message:
			cls.history( sender, DBConf.get( 'username' ), message )
			DBSchedule.set( 'messageActionTrigger', None, sender, message )
	
	@classmethod
	def presenceCallbackHook( cls, contact, status ):
		DBSchedule.set( 'statusActionTrigger', None, contact, status )
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
		#contactList = Transport.getContactList().items()
		for contact in contactList:
			DBSchedule.set( 'statusActionTrigger', None, contact, 'online' )
	
	@classmethod
	def refreshProjectList( cls ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project list' )
		#Transport.sendMessage( DBConf.get( 'bot' ), 'project list' )
		cls.messageCallbackHandler = cls._refreshProjectList
	
	@classmethod
	def _refreshProjectList( cls, sender, message ):
		projectList = [line.split( ': ', 1) for line in message.split('\n') if len(line.split( ': ', 1))==2]
		if cls.trigger.get( 'refreshProjectList', None):
			DBSchedule.set( cls.trigger['refreshProjectList'], None, projectList )
			del cls.trigger['refreshProjectList']
	
	@classmethod
	def _displayProjectInfo( cls, sender, message ):
		projectInfo = message
		message = unidecode( message ).split( ':', 1 )[1].strip()
		DBSchedule.set( 'projectDataActionTrigger', None, message )
	
	@classmethod
	def sendMessageHook( cls, recipient, message ):
		cls.send( recipient, message )
	
	@classmethod
	def showContactsHook( cls ):
		cls.refreshContactList()
	
	@classmethod
	def showProjectsHook( cls, **kwarg ):
		cls.refreshProjectList()
		if 'trigger' in kwarg.keys():
			cls.trigger['refreshProjectList'] = kwarg['trigger']
	
	@classmethod
	def pickContactHook( cls, contact ):
		#TODO load history
		messages = cls.getHistory( contact )
	
	@classmethod
	def pickProjectHook( cls, project ):
		Transport.execute( 'sendMessage', DBConf.get( 'bot' ), 'project define '+project )
		#Transport.sendMessage( DBConf.get( 'bot' ), 'project define '+project )
		cls.messageCallbackHandler = cls._displayProjectInfo
