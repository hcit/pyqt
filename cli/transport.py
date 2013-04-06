#!/usr/bin/python
# -*-coding: utf-8 -*-

import xmpp, time
from db import DBConf

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
	def messageCallback( cls, sender, text ):
		return True
	
	@classmethod
	def presenceCallback( cls, contact, status ):
		return True
	
	@classmethod
	def errorCallback( cls, e ):
		return True
	
	@classmethod
	def _connect( cls ):
		print '::TRANSPORT-CONNECT', cls.username, cls.passwd
		"""Set up a connection to xmpp server. Authenticate"""
		cls._client = xmpp.Client( DBConf.get( 'server' ) )
		#cls._client = xmpp.Client( DBConf.get( 'server' ), debug=[] )
		cls._client.connect( server=( DBConf.get( 'server' ), DBConf.get( 'port' ) ) )
		cls._status = cls._client.auth( cls.username, cls.passwd, DBConf.get( 'nickname' ) ) and True
		if cls._status is None:
			cls._client = None
			return None
		cls._client.RegisterHandler( 'message', cls.getMessage )
		cls._client.sendInitPresence(requestRoster=1)
		cls._set_process()
		cls._get_roster()
		#cls.sendMessage( DBConf.get( 'username' ), 'online' )
		cls._client.RegisterHandler( 'presence', cls.getPresence )
		return True
	
	@classmethod
	def _get_client( cls ):
		if not cls._client:
			cls._connect()
		return cls._client
	
	@classmethod
	def sendMessage( cls, to, messageText, messageType='chat' ):
		message = xmpp.Message( to + '@' + DBConf.get( 'server' ), messageText )
		message.setAttr( 'type', messageType )
		cls._get_client().send( message )
	
	"""
	@classmethod
	def setMessageCallback( cls, callback ):
		cls.messageCallback = callback
	"""
	
	@classmethod
	def getMessage( cls, session, message ):
		#sender = message.getFrom().getResource()
		sender = str( message.getFrom() ).split('@')[0]
		messageText = message.getBody()
		if cls.listener and hasattr( cls.listener, 'messageCallbackHook' ):
			cls.listener.messageCallbackHook( sender, messageText )
		cls.messageCallback( sender, messageText )
	
	"""
	@classmethod
	def setPresenceCallback( cls, callback ):
		cls.presenceCallback = callback
	"""
	
	@classmethod
	def getPresence( cls, session, presence ):
		sender = str( presence.getFrom() ).split('@')[0]
		status = presence.getStatus() or 'online'
		cls._contactList[sender] = status
		if cls.listener and hasattr( cls.listener, 'presenceCallbackHook' ):
			cls.listener.presenceCallbackHook( sender, status )
		cls.presenceCallback( sender, status )
	
	@classmethod
	def getContactList( cls ):
		cls._get_roster()
		return cls._contactList
	
	@classmethod
	def connectionError( cls, e ):
		if cls.listener and hasattr( cls.listener, 'errorCallbackHook' ):
			cls.listener.errorCallbackHook( e )
		cls.errorCallback( e )
	
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
		import threading
		cls._client_thread = threading.Thread( target=cls._process, args=( 1, ) )
		cls._client_thread.daemon = True
		cls._client_thread.start()
	
	@classmethod
	def _process( cls, arg=1 ):
		while 1:
			try:
				cls._get_client().Process( arg )
			except ValueError as e:
				cls.connectionError( e )
