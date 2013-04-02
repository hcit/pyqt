#!/usr/bin/python
# -*- conding: utf-8 -*-
from random import randint
import sys, shelve, time, datetime
from unidecode import unidecode
from PyQt4 import QtGui, QtCore
from wrap import Wrap
from conf import Conf

CONFIG_APPNAME = Conf.getConf( 'appname' )
CONFIG_SELF = Conf.getConf( 'username' )
CONFIG_BOT = Conf.getConf( 'bot' )



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
		self.build()
		DBJob.set( 'helloActionTrigger' )
	
	def build( self ):
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self.master )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.projectsAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Projects', self.master )
		self.projectsAction.setShortcut( 'Ctrl+P' )
		self.projectsAction.setStatusTip( 'Show projects' )
		self.projectsAction.triggered.connect( self.projectsActionCallback )
		
		self.chatAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Chat', self.master )
		self.chatAction.setShortcut( 'Ctrl+H' )
		self.chatAction.setStatusTip( 'Chat' )
		self.chatAction.triggered.connect( self.chatActionCallback )
	
	def projectsActionCallback( self ):
		self.master.View.projects().show()
		DBJob.set( 'projectListActionTrigger' )
	
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
		self.master.projects.setWindowTitle( project + ' - ' + CONFIG_APPNAME )
		DBJob.set( 'projectDataActionTrigger', None, project )
	
	def sendMessageCallback( self ):
		message = self.master.View.chatMessage().toPlainText()
		message = message
		if not message:
			return
		contact = self.master.View.contactList().value()
		self.master.View.contactItem( contact ).sendTo( message )
		self.master.View.chatDialog().message( str( time.time() ), CONFIG_SELF, message )
		self.master.View.chatMessage().clear()
		Wrap.send( contact, message.replace( '<br />', '\n' ).replace( '<br/>', '\n' ).replace( '<br>', '\n' ) )
	
	def projectListActionTrigger( self, projects ):
		for project, title in projects:
			self.master.View.projectItem( project, title )
	
	def projectDataActionTrigger( self, projectData ):
		project = self.master.View.projectList().value()
		self.master.View.projectData().show( project, projectData )
	
	def statusActionTrigger( self, contact, status ):
		self.master.View.contactItem( contact, status )
	
	def messageActionTrigger( self, contact, message ):
		self.master.View.contactItem( contact ).receiveFrom( message, str( time.time() ) )
		if self.master.View.contactList().value() == contact:
			self.master.View.chatDialog().message( time.time(), contact, message )
	
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
		#self.viewMenuControl.addAction( self.master.Action.chatAction )



class View:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.master.central = QtGui.QWidget()
		self.master.central.setStyleSheet( 'background: white' )
		self.master.central.resize( 250, 150 )
		self.master.central.move( 450, 450 )
		
		grid = QtGui.QGridLayout()
		grid.addWidget( self.contactFilter( self.master.central ), 0, 0 )
		grid.addWidget( self.contactList( self.master.central ), 1, 0 )
		self.master.central.setLayout( grid )
		
		self.master.setCentralWidget( self.master.central )
	
	#################### VIEW central ####################
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
	
	#################### VIEW projects ####################
	def projects( self ):
		if not hasattr( self.master, 'projects' ):
			self.master.projects = QtGui.QWidget()
			self.master.projects.setWindowTitle( 'Projects' + ' - ' + CONFIG_APPNAME )
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
			self.master.chat.setWindowTitle( self.master.View.contactList().value() + ' - ' + CONFIG_APPNAME )
			self.master.chat.resize( 350, 250 )
			self.master.chat.move( 450, 450 )
		
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



class RandomActionThread( QtCore.QThread ):
	randomData = {
		'project':(
			'IZI', 'ELIAS'
		),
		'contact':(
			'Ivan', 'Nick', 'Jack', 'Petr', 'Sam', 'Eugen', 'Alex', 'Bob', 'Viktor', 'Mo', 'Fred', 'Woo', 'Bradley', 'Dmitry', 'Jim', 'Lu', CONFIG_BOT, 
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
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':self.name, 'recipient':CONFIG_SELF, 'message':message }
		self.messagesNew[ts] = message
		self.update()
	
	def sendTo( self, message ):
		ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':CONFIG_SELF, 'recipient':self.name, 'message':message }



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
				( sender==CONFIG_SELF and '#000' or '#66f' ),
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
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':self.name, 'recipient':CONFIG_SELF, 'message':message }
		self.messagesNew[ts] = message
		self.update()
	
	def sendTo( self, message ):
		ts = str( time.time() )
		self.messagesTime.append( ts )
		self.messagesList[ts] = { 'ts':str( ts ), 'sender':CONFIG_SELF, 'recipient':self.name, 'message':message }


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
				( sender==CONFIG_SELF and '#000' or '#66f' ),
				sender,
				message
			)
		self.write( text )
	
	def plain( self, data ):
		if type( data ) == list:
			return '<ul>' + ''.join( ['<li>' + self.plain( i ) + '</li>' for i in data] ) + '</ul>'
		elif type( data ) == dict:
			return '<dl>' + ''.join( ['<dd>' + self.plain( k ) + '</dd>' + '<dt>' + self.plain( v ) + '</dt>' for k, v in data.items()] ) + '</dl>'
		else:
			return str( data )
	
	def show( self, project, projectData ):
		import json
		self.clear()
		data = '<table>'
		for k, v in json.loads( projectData ).items():
			data += '<tr>'
			data += '<th>' + str( k ) + '</th>'
			data += '<td>' + self.plain( v ) + '</td>'
			data += '</tr>'
		data += '</table>'
		text =  '<span style="font-weight:bold; color:#66f;">[%s]</span><br />%s<br />' % (
				project,
				data
			)
		self.write( text )



def main():
	app = QtGui.QApplication( sys.argv )
	ui = UI()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
