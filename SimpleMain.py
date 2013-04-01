#!/usr/bin/python
# -*- conding: utf-8 -*-
from random import randint
import sys, shelve, time
from unidecode import unidecode
from PyQt4 import QtGui, QtCore

class Main( QtGui.QMainWindow ):
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.build()
	
	def build( self ):
		self.setGeometry(50, 100, 300, 600)
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
		print '::pickContactActionCallback', contact, self.master.View.contactItem( contact ).messages()
		self.chatActionCallback()
		self.master.View.chatRightTextEdit.clear()
		for ts, message in self.master.View.contactItem( contact ).messages():
			self.master.View.chatRightTextEdit.write( '[%s] %s\n%s\n' % ( str(ts), contact, message ) )
	
	def statusActionTrigger( self, contact, status ):
		self.master.View.contactItem( contact, status )
	
	def messageActionTrigger( self, contact, message ):
		self.master.View.contactItem( contact ).messageSet( str(time.time()), message )
	
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
		#self.master.central.setWindowTitle( 'Text' )
		self.master.central.setStyleSheet( 'background: white' )
		self.master.central.resize(250, 150)
		self.master.central.move(450, 450)
		
		grid = QtGui.QGridLayout()
		grid.addWidget( self.contactFilter( self.master.central ), 0, 0 )
		grid.addWidget( self.contactList( self.master.central ), 1, 0 )
		self.master.central.setLayout( grid )
		
		self.master.setCentralWidget( self.master.central )
		
		#self.master.textEdit = QtGui.QTextEdit()
		#self.master.setCentralWidget( self.master.textEdit )
	
	def contactList( self, parent=None ):
		if not hasattr( self, '_contactList' ):
			self._contactList = QtGui.QGroupBox( 'Contacts', parent )
			self._contactList.layout = QtGui.QVBoxLayout()
			self._contactList.setLayout( self._contactList.layout )
			self._contactList.radioList = {}
			setattr( self._contactList, 'value', lambda:''.join( [k for k, w in self._contactList.radioList.items() if w.isChecked()] ) )
			self._contactList.setStyleSheet( 'background:black; color:white' )
			#self._contactList._textEdit = QtGui.QTextEdit( self._contactList )
			self._contactList.contactListItems = {}
		return self._contactList
	
	def contactItem( self, contact, status=None ):
		if not contact in self._contactList.radioList.keys():
			self._contactList.radioList[contact] = QtGui.QRadioButton( '' )
			self._contactList.radioList[contact].messageNew = []
			self._contactList.radioList[contact].messageTime = []
			self._contactList.radioList[contact].messageList = {}
			setattr( self._contactList.radioList[contact], 'update', lambda: self._contactList.radioList[contact].setText( '%s [%s] %s' % ( contact, self._contactList.radioList[contact].status, ( len( self._contactList.radioList[contact].messageNew ) and '('+str( len( self._contactList.radioList[contact].messageNew ) )+')' or '') ) ) )
			setattr( self._contactList.radioList[contact], 'messages', lambda: setattr( self._contactList.radioList[contact], 'messageNew', [] ) or self._contactList.radioList[contact].messageTime.sort() or [(ts,self._contactList.radioList[contact].messageList[ts]) for ts in self._contactList.radioList[contact].messageTime] )
			setattr( self._contactList.radioList[contact], 'messageSet', lambda ts,message: self._contactList.radioList[contact].messageTime.append(ts) or self._contactList.radioList[contact].messageList.update( {ts:message} ) or self._contactList.radioList[contact].messageNew.append( {ts:message} ) or self._contactList.radioList[contact].update() )
			self._contactList.radioList[contact].clicked.connect( self.master.Action.pickContactActionCallback )
			self._contactList.layout.addWidget( self._contactList.radioList[contact] )
			self._contactList.radioList[contact].status = '?'
		self._contactList.radioList[contact].status = status or self._contactList.radioList[contact].status
		self._contactList.radioList[contact].update()
		#self._contactList.radioList[contact].setText( '%s [%s] %s' % ( contact, self._contactList.radioList[contact].status, ( len( self._contactList.radioList[contact].messageNew ) and '('+str( len( self._contactList.radioList[contact].messageNew ) )+')' or '') ) )
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
			self.master.listView.resize(250, 150)
			self.master.listView.move(550, 550)
		
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
			self.master.chat.setStyleSheet( 'background: green' )
			self.master.chat.resize(250, 150)
			self.master.chat.move(450, 450)
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.chatDialog( self.master.chat ), 0, 0 )
			grid.addWidget( self.chatMessage( self.master.chat ), 1, 0 )
			self.master.chat.setLayout( grid )
		return self.master.chat
	
	def chatDialog( self, parent=None ):
		if not hasattr( self, '_chatDialog' ):
			self._chatDialog = QtGui.QWidget( parent )
			self._chatDialog.setStyleSheet( 'background: white' )
			self.chatRightTextEdit = QtGui.QTextEdit( self._chatDialog )
			self.chatRightTextEdit.setMaximumHeight( 1000 )
			self.chatRightTextEdit.setReadOnly(1)
			setattr( self.chatRightTextEdit, 'textCursor', QtGui.QTextCursor( self.chatRightTextEdit.document() ) )
			setattr( self.chatRightTextEdit, 'write', lambda text: self.chatRightTextEdit.textCursor.insertText( text + '\n' ) )
		return self._chatDialog
	
	def chatMessage( self, parent=None ):
		if not hasattr( self, '_chatMessage' ):
			self._chatMessage = QtGui.QWidget( parent )
			self._chatMessage.setStyleSheet( 'background: white' )
			chatLineEdit = QtGui.QLineEdit( self._chatMessage )
			chatLineEdit.setMaximumHeight( 1000 )
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
			getattr( self.master.Action, task['callback']+'Trigger' )( *task['arg'], **task['kwarg'] )
	
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
			'statusAction', 'messageAction', 'reportAction'
		)
	}
	
	@classmethod
	def getRandom( cls, dataType ):
		return cls.randomData[dataType][randint( 0, len( cls.randomData[dataType] ) - 1 )]
	
	@classmethod
	def statusAction( cls ):
		contact = cls.getRandom( 'contact' )
		status = cls.getRandom( 'status' )
		return ( [ contact, status ], {} )
	
	@classmethod
	def messageAction( cls ):
		contact = cls.getRandom( 'contact' )
		letters = 'abcdefghijklmnopqrstuvwxyz.,!?-   '
		message = ''.join( [letters[randint(0,len(letters)-1)] for i in range(0,randint(1, 1000))] )
		return ( [ contact, message ], {} )
	
	@classmethod
	def reportAction( cls ):
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
				print '::TASK', callback, None, arg, kwarg
				WorkThread.scheduleSet( callback, None, *arg, **kwarg )
			time.sleep( 0.4 )



def main():
	app = QtGui.QApplication( sys.argv )
	ui = Main()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
