#!/usr/bin/python
# -*- conding: utf-8 -*-
from random import randint
import sys, shelve, time
from unidecode import unidecode
from PyQt4 import QtGui, QtCore

CONFIG_SELF = 'Me'



class Main( QtGui.QMainWindow ):
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
		self.WorkThread = WorkThread( self )
		self.RandomActionThread = RandomActionThread()
		
		### Show the MainWindow
		self.show()



class Action:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self.master )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.listViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&List', self.master )
		self.listViewAction.setShortcut( 'Ctrl+L' )
		self.listViewAction.setStatusTip( 'List Files' )
		self.listViewAction.triggered.connect( self.listViewActionCallback )
		
		self.chatAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Text', self.master )
		self.chatAction.setShortcut( 'Ctrl+T' )
		self.chatAction.setStatusTip( 'Text Editor' )
		self.chatAction.triggered.connect( self.chatActionCallback )
	
	def listViewActionCallback( self ):
		self.master.View.listView().show()
	
	def chatActionCallback( self ):
		self.master.View.chat().show()
	
	def pickContactActionCallback( self ):
		contact = self.master.View.contactList().value()
		self.chatActionCallback()
		self.master.View.chatDialog().clear()
		for message in self.master.View.contactItem( contact ).messages():
			
			self.master.View.chatDialog().message( message['ts'], message['sender'], message['message'] )
	
	def sendMessageCallback( self ):
		message = self.master.View.chatMessage().toPlainText()
		if not message:
			return
		contact = self.master.View.contactList().value()
		self.master.View.contactItem( contact ).sendTo( message )
		self.master.View.chatDialog().message( str( time.time() ), CONFIG_SELF, message )
		self.master.View.chatMessage().clear()
	
	def statusActionTrigger( self, contact, status ):
		self.master.View.contactItem( contact, status )
	
	def messageActionTrigger( self, contact, message ):
		self.master.View.contactItem( contact ).receiveFrom( message, str( time.time() ) )
		#print '::messageAction', self.master.View.contactList().value()
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
		self.viewMenuControl.addAction( self.master.Action.listViewAction )
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
	
	def contactList( self, parent=None ):
		if not hasattr( self, '_contactList' ):
			self._contactList = QContactList( 'contacts', self.master.central )
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
	
	def listView( self ):
		if not hasattr( self.master, 'listView' ):
			self.master.listView = QtGui.QWidget()
			self.master.listView.setWindowTitle( 'List' )
			self.master.listView.setStyleSheet( 'background: blue' )
			self.master.listView.resize( 350, 250 )
			self.master.listView.move( 550, 550 )
		
			listViewLeft = QtGui.QWidget( self.master.listView )
			listViewLeft.setStyleSheet( 'background: black' )
			layout = QtGui.QVBoxLayout( listViewLeft )
			layout.addStretch(  )
			listViewLeft.setLayout( layout )
		
			listViewRight = QtGui.QWidget( self.master.listView )
			listViewRight.setStyleSheet( 'background: white' )
			layout = QtGui.QVBoxLayout( listViewRight )
			layout.addStretch(  )
			listViewRight.setLayout( layout )
		
			listViewSplitter = QtGui.QSplitter( QtCore.Qt.Horizontal, self.master.listView )
			listViewSplitter.addWidget( listViewLeft )
			listViewSplitter.addWidget( listViewRight )
		return self.master.listView
		
	def chat( self ):
		if not hasattr( self.master, 'chat' ):
			self.master.chat = QtGui.QWidget()
			self.master.chat.setWindowTitle( self.master.View.contactList().value() + ' - XMPP' )
			#self.master.chat.setStyleSheet( 'background: green' )
			self.master.chat.resize( 350, 250 )
			self.master.chat.move( 450, 450 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.chatDialog( self.master.chat ), 0, 0 )
			grid.addWidget( self.chatMessage( self.master.chat ), 1, 0 )
			self.master.chat.setLayout( grid )
		return self.master.chat
	
	def chatDialog( self, parent=None ):
		import datetime
		if not hasattr( self, '_chatDialog' ):
			self._chatDialog = QtGui.QTextEdit( parent )
			self._chatDialog.setMaximumHeight( 1000 )
			self._chatDialog.setReadOnly(1)
			setattr( self._chatDialog, 'textCursor', QtGui.QTextCursor( self._chatDialog.document() ) )
			setattr( self._chatDialog, 'write', lambda text: self._chatDialog.textCursor.insertHtml( text + '<br />' ) )
			setattr( self._chatDialog, 'message', lambda ts, sender, message: self._chatDialog.write( '<span style="color:#999;">[%s]</span> <span style="font-weight:bold; color:%s;">%s</span><br />%s<br />' % ( datetime.datetime.fromtimestamp( int( ts.split('.')[0] ) ).strftime('%Y-%m-%d %H:%M:%S'), (sender==CONFIG_SELF and '#000' or '#66f'), sender, message ) ) )
		return self._chatDialog
	
	def chatMessage( self, parent=None ):
		if not hasattr( self, '_chatMessage' ):
			self._chatMessage = QChatInput( '', parent )
			self._chatMessage.setMaximumHeight( 50 )
			#self._chatMessage.setStyleSheet( 'background: white' )
			self.master.connect( self._chatMessage, QtCore.SIGNAL( 'sendMessage' ), self.master.Action.sendMessageCallback )
		return self._chatMessage



class WorkThread( QtCore.QThread ):
	_cronPath = 'cron.db'
	_schedulePath = 'schedule.db'
	def __init__( self, master ):
		#TODO: create default scheduled tasks if file not exists
		QtCore.QThread.__init__( self )
		self.master = master
		self.schedule = shelve.open( self._schedulePath )
		self.build()
	
	def build( self ):
		self.master.connect( self, QtCore.SIGNAL( 'respond()' ), self.respond )
		self.start()
	
	def run( self ):
		while True:
			for ts, task in self.cronGet():
				self.scheduleSet( ts, task['callback'], *task['arg'], **task['kwarg'] )
			time.sleep( 0.3 ) # artificial time delay
			self.emit( QtCore.SIGNAL( 'respond()' ) )
	
	def respond( self ):
		for ts, task in self.scheduleGet():
			print '::RESPOND', ts, task
			getattr( self.master.Action, task['callback'] )( *task['arg'], **task['kwarg'] )
	
	@classmethod
	def cronGet( self ):
		cron = shelve.open( self._cronPath )
		taskList = []
		keys = cron.keys()
		keys.sort()
		for ts in keys:
			task = cron[ts]
			if float( ts ) < time.time():
				del cron[ts]
				cron[str( time.time() + task['period'] )] = task
				taskList.append( ( ts, task ) )
				self.scheduleSet( task['callback'], None, *task['arg'], **task['kwarg'] )
		cron.sync()
		cron.close()
		return taskList
	
	@classmethod
	def cronSet( self, callback, period, *arg, **kwarg ):
		cron = shelve.open( self._cronPath )
		cron[str( time.time() )] = {
			'period':period,
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		cron.sync()
		cron.close()
	
	@classmethod
	def scheduleGet( self ):
		schedule = shelve.open( self._schedulePath )
		taskList = []
		keys = schedule.keys()
		keys.sort()
		for ts in keys:
			task = schedule[ts]
			del schedule[ts]
			taskList.append( ( ts, task ) )
		schedule.sync()
		schedule.close()
		return taskList
	
	@classmethod
	def scheduleSet( self, callback, ts=None, *arg, **kwarg ):
		if not ts:
			ts = time.time()
		schedule = shelve.open( self._schedulePath )
		schedule[str( ts )] = {
			'callback':callback,
			'arg':arg,
			'kwarg':kwarg
		}
		schedule.sync()
		schedule.close()



class RandomActionThread( QtCore.QThread ):
	randomData = {
		'contact':(
			'Ivan', 'Nick', 'Jack', 'Petr', 'bot'
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
				#print '::TASK', callback, None, arg, kwarg
				WorkThread.scheduleSet( callback, None, *arg, **kwarg )
			time.sleep( 0.4 )



class QContactList( QtGui.QGroupBox ):
	def __init__( self, name, parent ):
		super( self.__class__, self ).__init__( name, parent )
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
		if self.isChecked():#if self.parent.value() == self.name:
			self.messagesNew = {}
		self.setText( '%s [%s] %s' % (
			self.name,
			self.status,
			len( self.messagesNew ) and '('+str( len( self.messagesNew ) )+')' or ''
		) )
	
	def messages( self, since=None ):
		#self.messagesNew = []
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



def main():
	app = QtGui.QApplication( sys.argv )
	ui = Main()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
