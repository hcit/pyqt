#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys
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
		import shelve
		QtCore.QThread.__init__( self )
		self.master = master
		self.schedule = shelve.open( self._schedulePath )
		self.build()
	
	def build( self ):
		self.master.connect( self, QtCore.SIGNAL( 'respond()' ), self.respond )
		self.start()
	
	def run( self ):
		import time
		while True:
			
			for ts, task in self.cron.keys():
				if float( ts ) < time.time():
					del self.cron[ts]
					self.cron[str( time.time() + task['period'] )] = task
					self.cron.sync()
					#TODO set task in execution stack
					if not task['callback'] in self.schedule.keys():
						self.schedule[task['callback']] = []
					schedule = self.schedule[task['callback']]
					schedule.append( task )
					self.schedule[task['callback']] = schedule
					self.schedule.sync()
			time.sleep( 0.3 ) # artificial time delay
			self.emit( QtCore.SIGNAL( 'respond()' ) )
	
	@classmethod
	def cronGet( self ):
		import time
		cron = shelve.open( self._cronPath )
		taskList = ()
		for ts, task in cron.keys():
			if float( ts ) < time.time():
				del cron[ts]
				cron[str( time.time() + task['period'] )] = task
				self.scheduleSet( None, task['callback'], *task['arg'], **task['kwarg'] )
		cron.sync()
		cron.close()
	
	@classmethod
	def cronSet( self, period, callback, *arg, **kwarg ):
		import time
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
		pass
	
	@classmethod
	def scheduleSet( self, ts=None, callback, *arg, **kwarg ):
		pass
	
	def respond( self ):
		pass



class RandomActionThread( QtCore.QThread ):
	def __init__( self ):
		QtCore.QThread.__init__( self )
		self.build()
	
	def build( self ):
		self.actions = {
			'contactList':[
				(
					( 'ivan', 'online' )
				),
			]
		}
		self.start()
	
	def run( self ):
		import time
		while True:
			time.sleep( 0.4 )



def main():
	RandomActionThread()
	app = QtGui.QApplication( sys.argv )
	ui = Main()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
