#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys, time, datetime
from PyQt4 import QtGui, QtCore

#from wrap import Wrap
from async import ListenerThread, ExecutionThread
from db import DBConf, DBJob, DBCron, DBSchedule



class UI( QtGui.QMainWindow ):
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.build()
	
	def build( self ):
		self.setGeometry( 50, 100, 300, 600 )
		self.setWindowTitle( 'Contacts' )    
		self.statusBar()
		
		self.Action = Action( self )
		### actions
		
		### Menus and Controls
		self.Control = Control( self )
		
		### Views
		self.View = View( self )
		
		### Thread
		self.ListenerThread = ListenerThread( self )
		self.ExecutionThread = ExecutionThread( self )
		#self.RandomActionThread = RandomActionThread()
		
		### Show the MainWindow
		self.show()



class Action:
	def __init__( self, master ):
		self.master = master
		# TODO: if no pref found, show preferences view
		# TODO: show login/store login and password preferences
		self.build()
	
	def build( self ):
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self.master )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.logoutAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Log &out', self.master )
		self.logoutAction.setShortcut( 'Ctrl+O' )
		self.logoutAction.setStatusTip( 'Log out' )
		self.logoutAction.triggered.connect( self.logoutActionCallback )
		
		self.preferencesAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Pre&ferences', self.master )
		self.preferencesAction.setShortcut( 'Ctrl+F' )
		self.preferencesAction.setStatusTip( 'Preferences' )
		self.preferencesAction.triggered.connect( self.preferencesActionCallback )
		
		self.projectsAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Projects', self.master )
		self.projectsAction.setShortcut( 'Ctrl+P' )
		self.projectsAction.setStatusTip( 'Show projects' )
		self.projectsAction.triggered.connect( self.projectsActionCallback )
		
		self.reportAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Send &Report', self.master )
		self.reportAction.setShortcut( 'Ctrl+R' )
		self.reportAction.setStatusTip( 'Report' )
		self.reportAction.triggered.connect( self.reportActionCallback )
		
		self.chatAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'C&hat', self.master )
		self.chatAction.setShortcut( 'Ctrl+H' )
		self.chatAction.setStatusTip( 'Chat' )
		self.chatAction.triggered.connect( self.chatActionCallback )
	
	def logoutActionCallback( self ):
		DBConf.set( 'username', '' )
		DBConf.set( 'passwd', '' )
		self.master.central().hide()
		self.master.login().show()
	
	def loginActionCallback( self ):
		#self.master.central().hide()
		self.master.View.login().show()
	
	def preferencesActionCallback( self ):
		self.master.View.preferences().show()
	
	def projectsActionCallback( self ):
		self.master.View.projects().show()
		DBJob.set( 'projectListActionTrigger', trigger='projectListActionTrigger' )
	
	def reportActionCallback( self ):
		self.master.View.report().show()
		DBJob.set( 'projectListActionTrigger', trigger='reportProjectListActionTrigger' )
	
	def chatActionCallback( self ):
		self.master.View.chat().show()
	
	def pickContactActionCallback( self ):
		contact = self.master.View.contactList().value()
		self.chatActionCallback()
		self.master.View.chatDialog().clear()
		for message in self.master.View.contactItem( contact ).messages():
			self.master.View.chatDialog().message( message['ts'], message['sender'], message['message'] )
	
	def pickProjectActionCallback( self ):
		project = self.master.View.projectList().value()
		self.master.projects.setWindowTitle( project + ' - ' + DBConf.get( 'appname' ) )
		DBJob.set( 'projectDataActionTrigger', None, project )
	
	def sendMessageCallback( self ):
		message = self.master.View.chatMessage().toPlainText()
		message = message
		if not message:
			return
		contact = self.master.View.contactList().value()
		self.master.View.contactItem( contact ).sendTo( message )
		self.master.View.chatDialog().message( str( time.time() ), DBConf.get( 'username' ), message )
		self.master.View.chatMessage().clear()
		DBJob.set( 'sendMessageActionTrigger', None, contact, message.replace( '<br />', '\n' ).replace( '<br/>', '\n' ).replace( '<br>', '\n' ) )
		#Wrap.send( contact, message.replace( '<br />', '\n' ).replace( '<br/>', '\n' ).replace( '<br>', '\n' ) )
	
	def loginSubmitCallback( self ):
		for k, v in self.master.View.login().fields.items():
			DBConf.set( k, type( DBConf.get( k ) )( v.text() ) )
			DBJob.set( 'connectActionTrigger' )
	
	def preferencesSubmitCallback( self ):
		for k, v in self.master.View.preferences().fields.items():
			DBConf.set( k, type( DBConf.get( k ) )( v.text() ) )
			self.master.View.preferences().hide()
	
	def preferencesCancelCallback( self ):
		self.master.View.preferences().hide()
	
	def projectListActionTrigger( self, projects ):
		for project, title in projects:
			self.master.View.projectItem( project, title )
	
	def projectDataActionTrigger( self, projectData ):
		project = self.master.View.projectList().value()
		self.master.View.projectData().show( project, projectData )
	
	def reportProjectListActionTrigger( self, projects ):
		self.master.View.reportProjectList().clear()
		for project, title in projects:
			self.master.View.reportProjectItem( project )
	
	def reportSubmitCallback( self ):
		data = dict( [( k, QHelper.getValue( v ) ) for k, v in self.master.View.report().fields.items()] )
		DBJob.set( 'reportActionTrigger', **data )
		self.master.View.report().hide()
	
	def reportCancelCallback( self ):
		self.master.View.report().hide()
	
	def statusActionTrigger( self, contact, status ):
		self.master.View.contactItem( contact, status )
	
	def messageActionTrigger( self, contact, message ):
		self.master.View.contactItem( contact ).receiveFrom( message, str( time.time() ) )
		if self.master.View.contactList().value() == contact:
			self.master.View.chatDialog().message( time.time(), contact, message )
	
	def errorActionTrigger( self, e ):
		self.master.Action.loginActionCallback()
		self.master.View.login().status.setText( str( e ) )
	
	def successActionTrigger( self ):
		self.master.View.login().hide()
		self.master.View.central().show()
		DBJob.set( 'helloActionTrigger' )
	
	def reportActionTrigger( self ):
		pass



class Control:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.menuControl = self.master.menuBar()
		self.fileMenuControl = self.menuControl.addMenu( '&File' )
		self.fileMenuControl.addAction( self.master.Action.exitAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.master.Action.projectsAction )
		self.viewMenuControl.addAction( self.master.Action.preferencesAction )
		self.actionMenuControl = self.menuControl.addMenu( '&Actions' )
		self.actionMenuControl.addAction( self.master.Action.reportAction )
		#self.viewMenuControl.addAction( self.master.Action.chatAction )



class View:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		#self.login().show()
		#self.central().show()
		self.login().show()
	
	#################### VIEW central ####################
	def central( self ):
		if not hasattr( self.master, 'central' ):
			self.master.central = QtGui.QWidget()
			self.master.central.setStyleSheet( 'background: white' )
			self.master.central.resize( 250, 150 )
			self.master.central.move( 450, 450 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.contactFilter( self.master.central ), 0, 0 )
			grid.addWidget( self.contactList( self.master.central ), 1, 0 )
			self.master.central.setLayout( grid )
			self.master.setCentralWidget( self.master.central )
		return self.master.central
	
	def contactList( self, parent=None ):
		if not hasattr( self, '_contactList' ):
			self._contactList = QContactList( self.master.central )
			self._contactList.setStyleSheet( 'background:black; color:white' )
		return self._contactList
	
	def contactItem( self, contact, status=None ):
		if not contact in self._contactList.radioList.keys():
			self._contactList.radioList[contact] = QContact( contact, self._contactList )
			self._contactList.radioList[contact].clicked.connect( self.master.Action.pickContactActionCallback )
			self._contactList.layout.addWidget( self._contactList.radioList[contact] )
		self._contactList.radioList[contact].status = status or self._contactList.radioList[contact].status
		self._contactList.radioList[contact].update()
		return self._contactList.radioList[contact]
	
	def contactFilter( self, parent=None ):
		if not hasattr( self, '_contactFilter' ):
			self._contactFilter = QtGui.QLineEdit( parent )
			self._contactFilter.setStyleSheet( 'background:black; color:white' )
		return self._contactFilter
	
	#################### VIEW login ####################
	def login( self ):
		if not hasattr( self.master, 'login' ):
			self.master.login = QtGui.QWidget()
			self.master.login.fields = {}
			self.master.login.setWindowTitle( 'Login' + ' - ' + DBConf.get( 'appname' ) )
			self.master.login.resize( 450, 200 )
			self.master.login.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			
			self.master.login.status = QtGui.QLabel( 'Please enter your login and password' )
			grid.addWidget( self.master.login.status, 0, 0, 2, 2 )
			
			grid.addWidget( QtGui.QLabel( 'username' ), 2, 0 )
			grid.addWidget( self.loginField( self.master.login, 'username', DBConf.get( 'username' ) ), 2, 1 )
			
			grid.addWidget( QtGui.QLabel( 'password' ), 3, 0 )
			grid.addWidget( self.loginField( self.master.login, 'passwd', DBConf.get( 'passwd' ) ), 3, 1 )
			
			self.master.login.submit = QtGui.QPushButton( 'Login', self.master.login )
			self.master.connect( self.master.login.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.loginSubmitCallback )
			grid.addWidget( self.master.login.submit, 4, 0 )
			
			self.master.login.quit = QtGui.QPushButton( 'Cancel', self.master.login )
			self.master.connect( self.master.login.quit, QtCore.SIGNAL( 'clicked()' ), QtGui.qApp.quit )
			grid.addWidget( self.master.login.quit, 4, 1 )
			
			self.master.login.preferences = QtGui.QPushButton( 'Preferences', self.master.login )
			self.master.connect( self.master.login.preferences, QtCore.SIGNAL( 'clicked()' ), lambda:self.master.View.login().hide() or self.master.Action.preferencesActionCallback() )
			grid.addWidget( self.master.login.preferences, 5, 0, 2 ,1 )
			
			self.master.login.setLayout( grid )
		return self.master.login
	
	def loginField( self, parent, key, value='' ):
		if not key in self.master.login.fields.keys():
			self.master.login.fields[key] = QtGui.QLineEdit( str( value ), parent )
		return self.master.login.fields[key]
	
	#################### VIEW projects ####################
	def projects( self ):
		if not hasattr( self.master, 'projects' ):
			self.master.projects = QtGui.QWidget()
			self.master.projects.setWindowTitle( 'Projects' + ' - ' + DBConf.get( 'appname' ) )
			self.master.projects.resize( 550, 450 )
			self.master.projects.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.projectData( self.master.projects ), 0, 0, 2, 1 )
			grid.addWidget( self.projectFilter( self.master.projects ), 0, 1 )
			grid.addWidget( self.projectList( self.master.projects ), 1, 1 )
			grid.setColumnMinimumWidth( 0, 300 )
			self.master.projects.setLayout( grid )
		return self.master.projects
	
	def projectData( self, parent=None ):
		if not hasattr( self, '_projectData' ):
			self._projectData = QProjectData( parent )
			self._projectData.setMaximumHeight( 1000 )
		return self._projectData
	
	def projectFilter( self, parent=None ):
		if not hasattr( self, '_projectFilter' ):
			self._projectFilter = QtGui.QLineEdit( parent )
			self._projectFilter.setStyleSheet( 'background:black; color:white' )
		return self._projectFilter
	
	def projectList( self, parent=None ):
		if not hasattr( self, '_projectList' ):
			self._projectList = QProjectList( self.master.projects )
			self._projectList.setStyleSheet( 'background:black; color:white' )
		return self._projectList
	
	def projectItem( self, project, status=None ):
		if not project in self._projectList.radioList.keys():
			self._projectList.radioList[project] = QProject( project, self._projectList )
			self._projectList.radioList[project].clicked.connect( self.master.Action.pickProjectActionCallback )
			self._projectList.layout.addWidget( self._projectList.radioList[project] )
		self._projectList.radioList[project].status = status or self._projectList.radioList[project].status
		self._projectList.radioList[project].update()
		return self._projectList.radioList[project]
	
	#################### VIEW chat ####################
	def chat( self ):
		if not hasattr( self.master, 'chat' ):
			self.master.chat = QtGui.QWidget()
			self.master.chat.setWindowTitle( self.master.View.contactList().value() + ' - ' + DBConf.get( 'appname' ) )
			self.master.chat.resize( 600, 450 )
			self.master.chat.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.chatDialog( self.master.chat ), 0, 0 )
			grid.addWidget( self.chatMessage( self.master.chat ), 1, 0 )
			self.master.chat.setLayout( grid )
		return self.master.chat
	
	def chatDialog( self, parent=None ):
		if not hasattr( self, '_chatDialog' ):
			self._chatDialog = QChatDialog( parent )
			self._chatDialog.setMaximumHeight( 1000 )
		return self._chatDialog
	
	def chatMessage( self, parent=None ):
		if not hasattr( self, '_chatMessage' ):
			self._chatMessage = QChatInput( '', parent )
			self._chatMessage.setMaximumHeight( 50 )
			self.master.connect( self._chatMessage, QtCore.SIGNAL( 'sendMessage' ), self.master.Action.sendMessageCallback )
		return self._chatMessage
	
	#################### VIEW preferences ####################
	def preferences( self ):
		if not hasattr( self.master, 'preferences' ):
			self.master.preferences = QtGui.QWidget()
			self.master.preferences.fields = {}
			self.master.preferences.setWindowTitle( 'Preferences' + ' - ' + DBConf.get( 'appname' ) )
			self.master.preferences.resize( 450, 550 )
			self.master.preferences.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			n = 0
			for key, value in DBConf.list():
				grid.addWidget( QtGui.QLabel( key ), n, 0 )
				grid.addWidget( self.preferencesField( self.master.preferences, key, value ), n, 1 )
				n += 1
			
			self.master.preferences.submit = QtGui.QPushButton( 'Save', self.master.preferences )
			self.master.connect( self.master.preferences.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.preferencesSubmitCallback )
			grid.addWidget( self.master.preferences.submit, n, 0 )
			
			self.master.preferences.cancel = QtGui.QPushButton( 'Cancel', self.master.preferences )
			self.master.connect( self.master.preferences.cancel, QtCore.SIGNAL( 'clicked()' ), self.master.Action.preferencesCancelCallback )
			grid.addWidget( self.master.preferences.cancel, n, 1 )
			
			self.master.preferences.setLayout( grid )
		return self.master.preferences
	
	def preferencesField( self, parent, key, value ):
		if not key in self.master.preferences.fields.keys():
			self.master.preferences.fields[key] = QtGui.QLineEdit( str( value ), parent )
		return self.master.preferences.fields[key]
	
	#################### VIEW report ####################
	def report( self ):
		if not hasattr( self.master, 'report' ):
			self.master.report = QtGui.QWidget()
			self.master.report.fields = {}
			self.master.report.setWindowTitle( 'Report' + ' - ' + DBConf.get( 'appname' ) )
			self.master.report.resize( 200, 200 )
			self.master.report.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			
			self.master.report.status = QtGui.QLabel( 'Report' )
			grid.addWidget( self.master.report.status, 0, 0, 2, 2 )
			
			grid.addWidget( self.reportField( self.master.report, 'h', 'hours' ), 2, 0 )
			
			grid.addWidget( self.reportField( self.master.report, 'm', 'minutes' ), 2, 1 )
			
			grid.addWidget( QtGui.QLabel( 'Project' ), 3, 0 )
			grid.addWidget( self.reportProjectList( self.master.report ), 3, 1 )
			
			grid.addWidget( QtGui.QLabel( 'Summary' ), 4, 0, 1, 2 )
			grid.addWidget( self.reportSummary( self.master.report, 'summary' ), 5, 0, 1, 2 )
			
			self.master.report.submit = QtGui.QPushButton( 'Send', self.master.report )
			self.master.connect( self.master.report.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.reportSubmitCallback )
			grid.addWidget( self.master.report.submit, 6, 0 )
			
			self.master.report.cancel = QtGui.QPushButton( 'Cancel', self.master.report )
			self.master.connect( self.master.report.cancel, QtCore.SIGNAL( 'clicked()' ), self.master.Action.reportCancelCallback )
			grid.addWidget( self.master.report.cancel, 6, 1 )
			
			self.master.report.setLayout( grid )
		return self.master.report
	
	def reportField( self, parent, key, placeholder='', value='' ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QLineEdit( str( value ), parent )
			self.master.report.fields[key].setPlaceholderText( placeholder )
		return self.master.report.fields[key]
	
	def reportSummary( self, parent, key ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QTextEdit( parent )
		return self.master.report.fields[key]
	
	def reportProjectList( self, parent=None ):
		if not hasattr( self, '_reportProjectList' ):
			self._reportProjectList = QtGui.QComboBox( parent )
			self.master.report.fields['project'] = self._reportProjectList
		return self._reportProjectList
	
	def reportProjectItem( self, value ):
		if hasattr( self, '_reportProjectList' ):
			self._reportProjectList.addItem( value )
	
	"""
	def projectFilter( self, parent=None ):
		if not hasattr( self, '_projectFilter' ):
			self._projectFilter = QtGui.QLineEdit( parent )
			self._projectFilter.setStyleSheet( 'background:black; color:white' )
		return self._projectFilter
	
	def projectList( self, parent=None ):
		if not hasattr( self, '_projectList' ):
			self._projectList = QProjectList( self.master.projects )
			self._projectList.setStyleSheet( 'background:black; color:white' )
		return self._projectList
	
	def projectItem( self, project, status=None ):
		if not project in self._projectList.radioList.keys():
			self._projectList.radioList[project] = QProject( project, self._projectList )
			self._projectList.radioList[project].clicked.connect( self.master.Action.pickProjectActionCallback )
			self._projectList.layout.addWidget( self._projectList.radioList[project] )
		self._projectList.radioList[project].status = status or self._projectList.radioList[project].status
		self._projectList.radioList[project].update()
		return self._projectList.radioList[project]
	"""



"""
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
			getattr( self.master.Action, task['callback'] )( *task['arg'], **task['kwarg'] )



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
	
	def helloActionTrigger( self ):
		Wrap.hello()
	
	def projectListActionTrigger( self ):
		#TODO: replace with wrapper.projectList
		#RandomActionThread.projectListAction()
		Wrap.showProjectsHook()
	
	def projectDataActionTrigger( self, project ):
		#TODO: replace with wrapper.projectData
		#RandomActionThread.projectDataAction( project )
		Wrap.pickProjectHook( project )
	
	def contactsActionTrigger( self ):
		#TODO: replace with wrapper.contactList
		#RandomActionThread.contactListAction()
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
"""



"""
class DBJob:
	__path = 'job.db'
	__handle = None
	
	@classmethod
	def handle( cls ):
		if cls.__handle is None:
			cls.__handle = shelve.open( cls.__path )
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		if cls.__handle is not None:
			cls.__handle.sync()
			cls.__handle.close()
			cls.__handle = None
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.handle().keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			del cls.handle()[ts]
			taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, ts=None, *arg, **kwarg ):
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()



class DBCron:
	__path = 'cron.db'
	__handle = None
	
	@classmethod
	def handle( cls ):
		if cls.__handle is None:
			cls.__handle = shelve.open( cls.__path )
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		if cls.__handle is not None:
			cls.__handle.sync()
			cls.__handle.close()
			cls.__handle = None
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.handle().keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			if float( ts ) < time.time():
				del cls.handle()[ts]
				cls.handle()[str( time.time() + task['period'] )] = task
				taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, period, *arg, **kwarg ):
		cls.handle()[str( time.time() )] = {
			'period':period,
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()



class DBSchedule:
	__path = 'schedule.db'
	__handle = None
	
	@classmethod
	def handle( cls ):
		if cls.__handle is None:
			cls.__handle = shelve.open( cls.__path )
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		if cls.__handle is not None:
			cls.__handle.sync()
			cls.__handle.close()
			cls.__handle = None
	
	@classmethod
	def get( cls ):
		taskList = []
		keys = cls.handle().keys()
		keys.sort()
		for ts in keys:
			task = cls.handle()[ts]
			del cls.handle()[ts]
			taskList.append( ( ts, task ) )
		cls.sync()
		return taskList
	
	@classmethod
	def set( cls, callback, ts=None, *arg, **kwarg ):
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cls.sync()
"""



class QContactList( QtGui.QGroupBox ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.radioList = {}
		self.contactListItems = {}
		self.layout = QtGui.QVBoxLayout()
		self.setLayout( self.layout )
	
	def value( self ):
		for k, w in self.radioList.items():
			if w.isChecked():
				return k



class QContact( QtGui.QRadioButton ):
	def __init__( self, name, parent ):
		super( self.__class__, self ).__init__( '' )
		self.name = name
		self.parent = parent
		self.messagesNew = {}
		self.messagesTime = []
		self.messagesList = {}
		self.status = '?'
	
	def update( self ):
		if self.isChecked():
			self.messagesNew = {}
		self.setText( '%s [%s] %s' % (
			self.name,
			self.status,
			len( self.messagesNew ) and '('+str( len( self.messagesNew ) )+')' or ''
		) )
	
	def messages( self, since=None ):
		self.messagesTime.sort()
		return [{ 'ts':ts, 'sender':self.messagesList[ts]['sender'], 'message':self.messagesList[ts]['message'] } for ts in self.messagesTime]
	
	def receiveFrom( self, message, ts=None ):
		if not ts:
			ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':self.name, 'recipient':DBConf.get( 'username' ), 'message':message }
		self.messagesNew[ts] = message
		self.update()
	
	def sendTo( self, message ):
		ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':DBConf.get( 'username' ), 'recipient':self.name, 'message':message }



class QChatDialog( QtGui.QTextEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.textCursor = QtGui.QTextCursor( self.document() )
		self.setReadOnly( 1 )
	
	def write( self, text ):
		self.textCursor.insertHtml( text + '<br />' )
	
	def message( self, ts, sender, message ):
		text =  '<span style="color:#999;">[%s]</span> <span style="font-weight:bold; color:%s;">%s</span><br />%s<br />' % (
				datetime.datetime.fromtimestamp( int( str( ts ).split('.')[0] ) ).strftime( '%Y-%m-%d %H:%M:%S' ),
				( sender==DBConf.get( 'username' ) and '#000' or '#66f' ),
				sender,
				message.replace( '\n', '<br />' )
			)
		self.write( text )



class QChatInput( QtGui.QTextEdit ):
	def __init__( self, text, parent ):
		super( self.__class__, self ).__init__( text, parent )
		self.parent = parent
		self.__sendMessageOnReturn = True
	
	def keyPressEvent( self, event ):
		if event.key() == QtCore.Qt.Key_Shift:
			self.__sendMessageOnReturn = False
		elif event.key() == QtCore.Qt.Key_Return:
			if self.__sendMessageOnReturn:
				self.emit( QtCore.SIGNAL( 'sendMessage' ) )
				return
		QtGui.QTextEdit.keyPressEvent( self, event )
	
	def keyReleaseEvent( self, event ):
		if event.key() == QtCore.Qt.Key_Shift:
			self.__sendMessageOnReturn = True
		QtGui.QTextEdit.keyPressEvent( self, event )



class QProjectList( QtGui.QGroupBox ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.radioList = {}
		self.projectListItems = {}
		self.layout = QtGui.QVBoxLayout()
		self.setLayout( self.layout )
	
	def value( self ):
		for k, w in self.radioList.items():
			if w.isChecked():
				return k



class QProject( QtGui.QRadioButton ):
	def __init__( self, name, parent ):
		super( self.__class__, self ).__init__( '' )
		self.name = name
		self.parent = parent
		self.messagesNew = {}
		self.messagesTime = []
		self.messagesList = {}
		self.status = '?'
	
	def update( self ):
		if self.isChecked():
			self.messagesNew = {}
		self.setText( '%s [%s] %s' % (
			self.name,
			self.status,
			len( self.messagesNew ) and '('+str( len( self.messagesNew ) )+')' or ''
		) )
	
	def messages( self, since=None ):
		self.messagesTime.sort()
		return [{ 'ts':ts, 'sender':self.messagesList[ts]['sender'], 'message':self.messagesList[ts]['message'] } for ts in self.messagesTime]
	
	def receiveFrom( self, message, ts=None ):
		if not ts:
			ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':self.name, 'recipient':DBConf.get( 'username' ), 'message':message }
		self.messagesNew[ts] = message
		self.update()
	
	def sendTo( self, message ):
		ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':DBConf.get( 'username' ), 'recipient':self.name, 'message':message }


class QProjectData( QtGui.QTextEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.textCursor = QtGui.QTextCursor( self.document() )
		self.setReadOnly( 1 )
	
	def write( self, text ):
		self.textCursor.insertHtml( text + '<br />' )
	
	def message( self, ts, sender, message ):
		text =  '<span style="color:#999;">[%s]</span> <span style="font-weight:bold; color:%s;">%s</span><br />%s<br />' % (
				datetime.datetime.fromtimestamp( int( str( ts ).split('.')[0] ) ).strftime( '%Y-%m-%d %H:%M:%S' ),
				( sender==DBConf.get( 'username' ) and '#000' or '#66f' ),
				sender,
				message
			)
		self.write( text )
	
	def plain( self, data ):
		if type( data ) == list:
			return '<ul style="margin:0; padding:0 0 0 15px;">' + ''.join( ['<li>' + self.plain( i ) + '</li>' for i in data] ) + '</ul>'
		elif type( data ) == dict:
			return '<dl style="margin:0; padding:0 0 0 15px;">' + ''.join( ['<dt style="font-weight:bold;">' + self.plain( k ) + '</dt>' + '<dd>' + self.plain( v ) + '</dd>' for k, v in data.items()] ) + '</dl>'
		else:
			return str( data )
	
	def show( self, project, projectData ):
		import json
		self.clear()
		data = '<table width="100%" cellspacing="4" cellpadding="0">'
		n=0
		for k, v in json.loads( projectData ).items():
			n+=1
			data += '<tr>'
			data += '<th style="background:'+(n%2 and '#f6f6f6' or '#fcfcfc')+';">' + str( k ) + '</th>'
			data += '<td style="">' + self.plain( v ) + '</td>'
			data += '</tr>'
		data += '</table>'
		text =  '<span style="font-weight:bold; color:#66f;">[%s]</span><br />%s<br />' % (
				project,
				data
			)
		self.write( text )



class QHelper:
	@classmethod
	def getValue( cls, widget ):
		if isinstance( widget, QtGui.QLineEdit ) or issubclass( widget.__class__, QtGui.QLineEdit ):
			return widget.text()
		elif isinstance( widget, QtGui.QComboBox ) or issubclass( widget.__class__, QtGui.QComboBox ):
			return widget.currentText()
		elif isinstance( widget, QtGui.QTextEdit ) or issubclass( widget.__class__, QtGui.QTextEdit ):
			return widget.toPlainText()



def main():
	app = QtGui.QApplication( sys.argv )
	ui = UI()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
