#!/usr/bin/python
# -*-coding: utf-8 -*-

import shelve, time, sys
from transport import Transport
from conf import Conf
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
	_dbs = {}
	messageCallbackHandler = None
	
	@classmethod
	def history( cls, sender, recipient, message ):
		if sender == Conf.getConf( 'username' ):
			name = recipient
		else:
			name = sender
		filename = 'history/' + Conf.getConf( 'username' ) + '_' + name + '.db'
		if not filename in cls._dbs.keys():
			cls._dbs[filename] = shelve.open( filename )
		cls._dbs[filename][str( time.time() )] = {'ts':str( int( time.time() ) ),'sender':_str(sender),'recipient':_str(recipient),'message':_str(message)}
		cls._dbs[filename].sync()
	
	@classmethod
	def getHistory( cls, contact ):
		filename = 'history/' + Conf.getConf( 'username' ) + '_' + contact + '.db'
		if not filename in cls._dbs.keys():
			cls._dbs[filename] = shelve.open( filename )
		keys = cls._dbs[filename].keys()
		keys.sort()
		return [cls._dbs[filename][key] for key in keys]
	
	@classmethod
	def hello( cls ):
		Transport.listener = cls
		Transport.sendMessage( Conf.getConf( 'username' ), 'online' )
	
	@classmethod
	def help( cls ):
		Transport.sendMessage( Conf.getConf( 'bot' ), 'help' )
	
	@classmethod
	def send( cls, to, message ):
		cls.history( Conf.getConf( 'username' ), to, message )
		Transport.sendMessage( _str( to ), _str( message ) )
	
	@classmethod
	def messageCallbackHook( cls, sender, message ):
		from ui import DBSchedule
		if not sender in Transport.getContactList().keys():
			sender = Conf.getConf( 'bot' )
		if cls.messageCallbackHandler is not None:
			cls.messageCallbackHandler( sender, message )
			cls.messageCallbackHandler = None
			return
		cls.history( sender, Conf.getConf( 'username' ), message )
		DBSchedule.set( 'messageActionTrigger', None, sender, message )
	
	@classmethod
	def presenceCallbackHook( cls, contact, status ):
		from ui import DBSchedule
		DBSchedule.set( 'statusActionTrigger', None, contact, status )
		#TODO??????????????? cls.refreshContactList()
	
	@classmethod
	def contacts( cls ):
		pass
	
	
	
	@classmethod
	def refreshContactList( cls ):
		from ui import DBSchedule
		contactList = Transport.getContactList().items()
		print '::CONTACTLIST', contactList
		for contact in contactList:
			DBSchedule.set( 'statusActionTrigger', None, contact, 'online' )
	
	@classmethod
	def refreshProjectList( cls ):
		Transport.sendMessage( Conf.getConf( 'bot' ), 'project list' )
		cls.messageCallbackHandler = cls._refreshProjectList
	
	@classmethod
	def _refreshProjectList( cls, sender, message ):
		from ui import DBSchedule
		projectList = [line.split( ': ', 1) for line in message.split('\n') if len(line.split( ': ', 1))==2]
		DBSchedule.set( 'projectListActionTrigger', None, projectList )
	
	@classmethod
	def _displayProjectInfo( cls, sender, message ):
		from ui import DBSchedule
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
	def showProjectsHook( cls ):
		cls.refreshProjectList()
	
	@classmethod
	def pickContactHook( cls, contact ):
		#TODO load history
		messages = cls.getHistory( contact )
	
	@classmethod
	def pickProjectHook( cls, project ):
		Transport.sendMessage( Conf.getConf( 'bot' ), 'project define '+project )
		cls.messageCallbackHandler = cls._displayProjectInfo
