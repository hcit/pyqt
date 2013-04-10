#!/usr/bin/python
# -*-coding: utf-8 -*-

import xmpp, time, threading
from dbs import DBConf
from helper import QHelper

class Transport:
	_client = None
	_roster = None
	_status = None
	_contactList = {}
	listener = None
	conf = {
		'username':'',
		'paswd':'',
		'nickname':'',
		'server':'',
		'port':0,
	}
	
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
	def presenceCallback( cls, contact, status, message ):
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
	def _connect( cls, username=None, passwd=None, conf={} ):
		if username:
			cls.conf['username'] = username
		if passwd:
			cls.conf['passwd'] = passwd
		if conf.get( 'server', None ):
			cls.conf['server'] = conf['server']
		if conf.get( 'port', None ):
			cls.conf['port'] = conf['port']
		if conf.get( 'nickname', None ):
			cls.conf['nickname'] = conf['nickname']
		print '::TRANSPORT-CONNECT', cls.conf
		"""Set up a connection to xmpp server. Authenticate"""
		#cls._client = xmpp.Client( cls.conf['server'] )
		cls._client = xmpp.Client( cls.conf['server'], debug=[] )
		cls._client.connect( server=( cls.conf['server'], cls.conf['port'] ) )
		cls._status = cls._client.auth( cls.conf['username'], cls.conf['passwd'], cls.conf['nickname'] ) and True
		if cls._status is None:
			cls._client = None
			
			if cls.listener and hasattr( cls.listener, 'connectErrorCallbackHook' ):
				cls.listener.connectErrorCallbackHook()
			cls.connectErrorCallback()
			
			return None
		cls._client.RegisterHandler( 'message', cls.getMessage )
		cls._client.RegisterHandler( 'presence', cls.getPresence )
		# http://stackoverflow.com/questions/2381597/xmpp-chat-accessing-contacts-status-messages-with-xmpppys-roster
		cls._client.sendInitPresence( requestRoster=1 )
		cls._set_process()
		cls._get_roster()
		
		if cls.listener and hasattr( cls.listener, 'connectSuccessCallbackHook' ):
			cls.listener.connectSuccessCallbackHook()
		cls.connectSuccessCallback()
		
		return True
	
	@classmethod
	def _reconnect( cls ):
		cls._client = None
		cls._connect()
	
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
		message = xmpp.Message( recipient + '@' + cls.conf['server'], messageText )
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
		#print '::ROSTER:STATUS_FOR', presence.getFrom(), str( presence.getFrom() ).split('/')[0]
		#print '::ROSTER:STATUS', cls._roster.getStatus( presence.getFrom().getStripped() )
		contact = str( presence.getFrom() ).split('@')[0]
		status = presence.getType() or presence.getShow() or 'online'
		message = presence.getStatus() or ''
		"""
		print '::PRESENCE:STATUS', {
			'getFrom':presence.getFrom(),
			'getFrom.getStripped':presence.getFrom().getStripped(),
			'getType':presence.getType(),
			'getShow':presence.getShow(),
			'getStatus':presence.getStatus()
		}
		"""
		cls._contactList[contact] = status
		if cls.listener and hasattr( cls.listener, 'presenceCallbackHook' ):
			cls.listener.presenceCallbackHook( contact, status, message )
		cls.presenceCallback( contact, status, message )
	
	"""
	@classmethod
	def getContactList( cls ):
		cls._get_roster()
		return cls._contactList
	"""
	
	@classmethod
	def _get_roster( cls ):
		return
		if cls._client and not cls._roster:
			QHelper.log( '::TRANSPORT:GET_ROSTER' )
			try:
				cls._roster = cls._get_client().getRoster()
				QHelper.log( '::TRANSPORT:GET_ROSTER:OK', cls._roster )
			except Exception as e:
				QHelper.log( '::TRANSPORT:GET_ROSTER:EXCEPTION', e )
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
				QHelper.log( '::TRANSPORT:PROCESS:VALUEERROR', e, LEVEL=QHelper.LOG_LEVEL_ERROR )
				cls.serverError( e )
			"""
			except Exception as e:
				QHelper.log( '::TRANSPORT:PROCESS:EXCEPTION', e, LEVEL=QHelper.LOG_LEVEL_ERROR )
				#cls._reconnect()
			"""
