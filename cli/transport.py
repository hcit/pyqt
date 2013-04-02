#!/usr/bin/python
# -*-coding: utf-8 -*-

import xmpp, time
from conf import Conf

class Transport:
	_client = None
	_roster = None
	_contactList = {}
	listener = None
	
	@classmethod
	def messageCallback( cls, sender, text ):
		return True
	
	@classmethod
	def presenceCallback( cls, contact, status ):
		return True
	
	@classmethod
	def _connect( cls ):
		"""Set up a connection to xmpp server. Authenticate"""
		cls._client = xmpp.Client( Conf.getConf( 'server' ) )
		cls._client.connect( server=( Conf.getConf( 'server' ), Conf.getConf( 'port' ) ) )
		cls._client.auth( Conf.getConf( 'username' ), Conf.getConf( 'passwd' ), Conf.getConf( 'nickname' ) )
		cls._client.RegisterHandler( 'message', cls.getMessage )
		cls._client.sendInitPresence(requestRoster=1)
		cls._set_process()
		cls._get_roster()
		cls.sendMessage( Conf.getConf( 'username' ), 'online' )
		cls._client.RegisterHandler( 'presence', cls.getPresence )
	
	@classmethod
	def _get_client( cls ):
		if not cls._client:
			cls._connect()
		return cls._client
	
	@classmethod
	def sendMessage( cls, to, messageText, messageType='chat' ):
		message = xmpp.Message( to + '@' + Conf.getConf( 'server' ), messageText )
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
			cls._get_client().Process( arg )
