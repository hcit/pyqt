#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

class SimpleMain( QtGui.QWidget ):
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.build()
	
	def build( self ):
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('Menubar')    
		"""
		self.statusBar()
		"""
		
		### actions
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.listViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&List', self )
		self.listViewAction.setShortcut( 'Ctrl+L' )
		#self.listViewAction.setStatusTip( 'List Files' )
		self.listViewAction.triggered.connect( self.listViewActionCallback )
		
		self.textViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Text', self )
		self.textViewAction.setShortcut( 'Ctrl+T' )
		#self.textViewAction.setStatusTip( 'Text Editor' )
		self.textViewAction.triggered.connect( self.textViewActionCallback )
		
		### Menus and Controls
		"""
		self.menuControl = self.menuBar()
		self.fileMenuControl = self.menuControl.addMenu( '&File' )
		self.fileMenuControl.addAction( self.exitAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.listViewAction )
		self.viewMenuControl.addAction( self.textViewAction )
		"""
		
		### container Widget
		self.container = QtGui.QWidget( self )
		#layout = QtGui.QHBoxLayout()
		#layout.addStretch( 1 )
		#self.container.setLayout( layout )
		self.container.setStyleSheet('color: blue')
		#self.setCentralWidget( self.container )
		self.text = QtGui.QLineEdit( "asd", self )
		
		### list Widget
		leftListWidget = QtGui.QWidget( self )
		leftListWidget.setStyleSheet('color: green')
		layout = QtGui.QVBoxLayout( leftListWidget )
		layout.addStretch( 1 )
		leftListWidget.setLayout( layout )
		
		rightListWidget = QtGui.QWidget( self )
		rightListWidget.setStyleSheet('color: red')
		layout = QtGui.QVBoxLayout( rightListWidget )
		layout.addStretch( 1 )
		rightListWidget.setLayout( layout )
		
		self.listWidget = QtGui.QSplitter( QtCore.Qt.Horizontal, self )
		self.listWidget.addWidget( leftListWidget )
		self.listWidget.addWidget( rightListWidget )
		
		### text Widget
		"""
		leftTextWidget = QtGui.QWidget( self )
		leftTextWidget.setStyleSheet('color: green')
		layout = QtGui.QVBoxLayout( leftTextWidget )
		layout.addStretch( 1 )
		leftTextWidget.setLayout( layout )
		"""
		leftTextWidget = QtGui.QFrame( self )
		leftTextWidget.setFrameShape( QtGui.QFrame.StyledPanel )
		
		#rightTextWidget = QtGui.QWidget( self )
		#rightTextWidget.setStyleSheet('color: red')
		#layout = QtGui.QVBoxLayout( rightTextWidget )
		#layout.addStretch( 1 )
		#rightTextWidget.setLayout( layout )
		rightTextWidget = QtGui.QFrame( self )
		rightTextWidget.setFrameShape( QtGui.QFrame.StyledPanel )
		
		self.textWidget = QtGui.QSplitter( QtCore.Qt.Horizontal, self )
		self.textWidget.addWidget( leftTextWidget )
		self.textWidget.addWidget( rightTextWidget )
		
		### Show the MainWindow
		self.textViewActionCallback()
		self.show()
	
	def listViewActionCallback( self ):
		self.listWidget.show()
		self.textWidget.hide()
	
	def textViewActionCallback( self ):
		self.listWidget.hide()
		self.textWidget.show()



def main():
	app = QtGui.QApplication( sys.argv )
	ui = SimpleMain()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
