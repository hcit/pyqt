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
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('Menubar')    
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
		
		self.textViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Text', self.master )
		self.textViewAction.setShortcut( 'Ctrl+T' )
		self.textViewAction.setStatusTip( 'Text Editor' )
		self.textViewAction.triggered.connect( self.textViewActionCallback )
	
	def listViewActionCallback( self ):
		self.master.View.listView().show()
	
	def textViewActionCallback( self ):
		self.master.View.textView().show()



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
		self.viewMenuControl.addAction( self.master.Action.textViewAction )



class View:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.master.textEdit = QtGui.QTextEdit()
		self.master.setCentralWidget( self.master.textEdit )
	
	def listView( self ):
		if not hasattr( self.master, 'listView' ):
			self.master.listView = QtGui.QWidget()
			self.master.listView.setWindowTitle( 'List' )
			self.master.listView.setStyleSheet('background: blue')
			self.master.listView.resize(250, 150)
			self.master.listView.move(550, 550)
		
			listViewLeft = QtGui.QWidget( self.master.listView )
			listViewLeft.setStyleSheet('background: black')
			layout = QtGui.QVBoxLayout( listViewLeft )
			layout.addStretch(  )
			listViewLeft.setLayout( layout )
		
			listViewRight = QtGui.QWidget( self.master.listView )
			listViewRight.setStyleSheet('background: white')
			layout = QtGui.QVBoxLayout( listViewRight )
			layout.addStretch(  )
			listViewRight.setLayout( layout )
		
			listViewSplitter = QtGui.QSplitter( QtCore.Qt.Horizontal, self.master.listView )
			listViewSplitter.addWidget( listViewLeft )
			listViewSplitter.addWidget( listViewRight )
		return self.master.listView
		
	def textView( self ):
		if not hasattr( self.master, 'textView' ):
			self.master.textView = QtGui.QWidget()
			self.master.textView.setWindowTitle( 'Text' )
			self.master.textView.setStyleSheet('background: green')
			self.master.textView.resize(250, 150)
			self.master.textView.move(450, 450)
		
			textViewLeft = QtGui.QWidget( self.master.textView )
			textViewLeft.setStyleSheet('background: black')
			textViewLeftTextEdit = QtGui.QTextEdit( textViewLeft )
			textViewLeftTextEdit.setMaximumHeight( 1000 )
		
			textViewRight = QtGui.QWidget( self.master.textView )
			textViewRight.setStyleSheet('background: white')
			textViewRightTextEdit = QtGui.QTextEdit( textViewRight )
			textViewRightTextEdit.setMaximumHeight( 1000 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( textViewLeft, 0, 0 )
			grid.addWidget( textViewRight, 0, 1)
			self.master.textView.setLayout( grid )
		return self.master.textView



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
			del task['period']
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
			'\xd0\x98\xd0\xb2\xd0\xb0\xd0\xbd', 'Nick', 'Jack', '\xd0\x90\xd0\xbb\xd0\xb5\xd0\xba\xd1\x81\xd0\xb5\xd0\xb9', 'bot'
		),
		'status':(
			'online', 'away', 'busy', 'unavailable', 'offline'
		),
		'callback':(
			'statusAction', 'contactListAction', 'messageAction', 'reportAction'
		)
	}
	
	@classmethod
	def getRandom( cls, dataType ):
		return cls.randomData[dataType][randint( 0, len( cls.randomData[dataType] ) - 1 )]
	
	@classmethod
	def contactListAction( cls ):
		return [( 'statusAction', [ contact, cls.getRandom( 'status' ) ], {} ) for contact in cls.randomData['contact'] ]
	
	@classmethod
	def statusAction( cls ):
		contact = cls.getRandom( 'contact' )
		status = cls.getRandom( 'status' )
		return ( [ 'statusAction', [ contact, status ], {} ] )
	
	@classmethod
	def messageAction( cls ):
		contact = cls.getRandom( 'contact' )
		letters = 'abcdefghijklmnopqrstuvwxyz.,!?-   '
		message = ''.join( [letters[randint(0,len(letters)-1)] for i in range(0,randint(1, 1000))] )
		return ( [ 'messageAction', [ contact, message ], {} ] )
	
	@classmethod
	def reportAction( cls ):
		return ( [ 'reportAction', [], {} ] )
	
	def __init__( self ):
		QtCore.QThread.__init__( self )
		self.build()
	
	def build( self ):
		self.start()
	
	def run( self ):
		while True:
			# if random returns a "trigger" value we run a random action
			if randint( 0, 10 ) == 1:
				callback = self.getRandom( 'callback' )
				for action, arg, kwarg in getattr( self, callback )():
					print '::TASK', callback, arg, kwarg
			time.sleep( 0.4 )



def main():
	app = QtGui.QApplication( sys.argv )
	ui = Main()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
