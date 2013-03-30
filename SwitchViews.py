#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

class UI( QtGui.QMainWindow ):
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.build()
	
	def build( self ):
		self.Action = Action( self )
		self.Control = Control( self )
		self.View = View( self )
		
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('Menubar')    
		self.show()



class UIElement:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		pass



class Action:
	def build( self ):
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self.master )        
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.listViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&List', self.master )        
		self.listViewAction.setShortcut( 'Ctrl+L' )
		self.listViewAction.setStatusTip( 'List Files' )
		self.listViewAction.triggered.connect( self.master.Action.listViewActionCallback )
		
		self.textViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Text', self.master )        
		self.textViewAction.setShortcut( 'Ctrl+T' )
		self.textViewAction.setStatusTip( 'Text Editor' )
		self.textViewAction.triggered.connect( self.master.Action.textViewActionCallback )
		
		self.master.statusBar()
	
	def listViewActionCallback( self ):
		self.master.View.display( 'list' )
	
	def textViewActionCallback( self ):
		self.master.View.display( 'text' )



class Control:
	def build( self ):
		self.menuControl = self.master.menuBar()
		self.fileMenuControl = self.menuControl.addMenu( '&File' )
		self.fileMenuControl.addAction( self.master.Action.exitAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.master.Action.listViewAction )
		self.viewMenuControl.addAction( self.master.Action.textViewAction )



class View:
	__views = {}
	widget = None
	
	def build( self ):
		self.widget = QtGui.QWidget( self.master )
		layout = QtGui.QBoxLayout()
		layout.addStretch( 1 )
		self.widget.setLayout( layout )
	
	def display( self, viewName ):
		if viewName == 'list':
			if not 'list' in self.__views.keys():
				self.__views['list'] = QtGui.QWidget( self.widget )
				



def main():
	app = QtGui.QtApplication()
	ui = UI()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
