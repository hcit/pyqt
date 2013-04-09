#!/usr/bin/python
# -*-coding: utf-8 -*-

import xmpp, time, threading
from dbs import DBConf

class Transport:
	_client = None
	_roster = None
	_status = None
	_contactList = {}
	listener = None
	username = None
	passwd = None
	
	@classmethod
	def execute( cls, action, *arg, **kwarg ):
		if hasattr( cls, action ) and callable( getattr( cls, action ) ):
			try:
				return getattr( cls, action )( *arg, **kwarg )
			except Exception as e:
				print '::TRANSPORT EXCEPTION', e
	
	@classmethod
	def sendMessageCallback( cls, recipient, message ):
		return True
	
	@classmethod
	def getMessageCallback( cls, sender, message ):
		return True
	
	@classmethod
	def presenceCallback( cls, contact, status ):
		return True
	
	@classmethod
	def serverErrorCallback( cls, e ):
		return True
	
	@classmethod
	def connectSuccessCallback( cls ):
		return True
	
	@classmethod
	def connectErrorCallback( cls ):
		return True
	
	@classmethod
	def _connect( cls, username=None, passwd=None ):
		if username:
			cls.username = username
		if passwd:
			cls.passwd = passwd
		print '::TRANSPORT-CONNECT', cls.username, cls.passwd
		"""Set up a connection to xmpp server. Authenticate"""
		#cls._client = xmpp.Client( DBConf.get( 'server' ) )
		cls._client = xmpp.Client( DBConf.get( 'server' ), debug=[] )
		cls._client.connect( server=( DBConf.get( 'server' ), DBConf.get( 'port' ) ) )
		cls._status = cls._client.auth( cls.username, cls.passwd, DBConf.get( 'nickname' ) ) and True
		if cls._status is None:
			cls._client = None
			
			if cls.listener and hasattr( cls.listener, 'connectErrorCallbackHook' ):
				cls.listener.connectErrorCallbackHook()
			cls.connectErrorCallback()
			
			return None
		cls._client.RegisterHandler( 'message', cls.getMessage )
		cls._client.sendInitPresence(requestRoster=1)
		cls._set_process()
		cls._get_roster()
		#cls.sendMessage( DBConf.get( 'username' ), 'online' )
		cls._client.RegisterHandler( 'presence', cls.getPresence )
		
		if cls.listener and hasattr( cls.listener, 'connectSuccessCallbackHook' ):
			cls.listener.connectSuccessCallbackHook()
		cls.connectSuccessCallback()
		
		return True
	
	@classmethod
	def _get_client( cls ):
		if not cls._client:
			cls._connect()
		return cls._client
	
	@classmethod
	def serverError( cls, e ):
		if cls.listener and hasattr( cls.listener, 'serverErrorCallbackHook' ):
			cls.listener.serverErrorCallbackHook( e )
		cls.serverErrorCallback( e )
	
	@classmethod
	def sendMessage( cls, recipient, messageText, messageType='chat' ):
		message = xmpp.Message( recipient + '@' + DBConf.get( 'server' ), messageText )
		message.setAttr( 'type', messageType )
		cls._get_client().send( message )
		if cls.listener and hasattr( cls.listener, 'sendMessageCallbackHook' ):
			cls.listener.sendMessageCallbackHook( recipient, messageText )
		cls.sendMessageCallback( recipient, messageText )
	
	@classmethod
	def getMessage( cls, session, message ):
		#sender = message.getFrom().getResource()
		sender = str( message.getFrom() ).split('@')[0]
		messageText = message.getBody()
		if cls.listener and hasattr( cls.listener, 'getMessageCallbackHook' ):
			cls.listener.getMessageCallbackHook( sender, messageText )
		cls.getMessageCallback( sender, messageText )
	
	@classmethod
	def getPresence( cls, session, presence ):
		contact = str( presence.getFrom() ).split('@')[0]
		status = presence.getStatus() or 'online'
		cls._contactList[contact] = status
		if cls.listener and hasattr( cls.listener, 'presenceCallbackHook' ):
			cls.listener.presenceCallbackHook( contact, status )
		cls.presenceCallback( contact, status )
	
	@classmethod
	def getContactList( cls ):
		cls._get_roster()
		return cls._contactList
	
	@classmethod
	def _get_roster( cls ):
		if cls._roster is None:
			try:
				pass#cls._roster = cls._get_client().getRoster()
			except Exception as e:
				pass
		return cls._roster
	
	@classmethod
	def _set_process( cls ):
		cls._client_thread = threading.Thread( target=cls._process, args=( 1, ) )
		cls._client_thread.daemon = True
		cls._client_thread.start()
	
	@classmethod
	def _process( cls, arg=1 ):
		while 1:
			try:
				cls._get_client().Process( arg )
			except ValueError as e:
				cls.serverError( e )
