#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

class SwitchViews( QtGui.QMainWindow ):
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

class UIWidget( QtGui.QWidget ):
	def __init__( self, master ):
		super( UIWidget, self ).__init__()
		self.master = master
		self.build()
	
	def build( self ):
		pass



class Action( UIElement ):
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
		
		self.master.statusBar()
	
	def listViewActionCallback( self ):
		self.master.View.display( 'list' )
	
	def textViewActionCallback( self ):
		self.master.View.display( 'text' )



class Control( UIElement ):
	def build( self ):
		self.menuControl = self.master.menuBar()
		self.fileMenuControl = self.menuControl.addMenu( '&File' )
		self.fileMenuControl.addAction( self.master.Action.exitAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.master.Action.listViewAction )
		self.viewMenuControl.addAction( self.master.Action.textViewAction )



class View( UIWidget ):
	__views = {}
	
	def build( self ):
		layout = QtGui.QHBoxLayout()
		layout.addStretch( 1 )
		self.setLayout( layout )
		self.master.setCentralWidget( self )
	
	def display( self, viewName ):
		
		if viewName == 'list':
			if not 'list' in self.__views.keys():
				self.__views['list'] = ViewListView( self )
		elif viewName == 'text':
			if not 'text' in self.__views.keys():
				self.__views['text'] = ViewListView( self )
		
		for key in self.__views.keys():
			if key == viewName:
				self.__views[key].show()
			else:
				self.__views[key].hide()

class ViewListView( View ):
	def build( self ):
		layout = QtGui.QVBoxLayout( self )
		layout.addStretch( 1 )
		self.setLayout( layout )
		leftWidget = self.leftWidget()
		rightWidget = self.rightWidget()
		splitter = QtGui.QSplitter( QtCore.Qt.Horizontal, self.master )
		splitter.addWidget( leftWidget )
		splitter.addWidget( rightWidget )
		#self.addWidget( splitter )
	
	def leftWidget( self ):
		widget = QtGui.QWidget( self.master )
		widget.setStyleSheet('color: green')
		layout = QtGui.QVBoxLayout( widget )
		layout.addStretch( 1 )
		widget.setLayout( layout )
		return widget
	
	def rightWidget( self ):
		widget = QtGui.QWidget( self.master )
		widget.setStyleSheet('color: red')
		layout = QtGui.QVBoxLayout( widget )
		layout.addStretch( 1 )
		widget.setLayout( layout )
		return widget
	



def main():
	app = QtGui.QApplication( sys.argv )
	ui = SwitchViews()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
