#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

class SimpleMain( QtGui.QMainWindow ):
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.build()
	
	def build( self ):
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('Menubar')    
		self.statusBar()
		
		### actions
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.listViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&List', self )
		self.listViewAction.setShortcut( 'Ctrl+L' )
		self.listViewAction.setStatusTip( 'List Files' )
		self.listViewAction.triggered.connect( self.listViewActionCallback )
		
		self.textViewAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Text', self )
		self.textViewAction.setShortcut( 'Ctrl+T' )
		self.textViewAction.setStatusTip( 'Text Editor' )
		self.textViewAction.triggered.connect( self.textViewActionCallback )
		
		### Menus and Controls
		self.menuControl = self.menuBar()
		self.fileMenuControl = self.menuControl.addMenu( '&File' )
		self.fileMenuControl.addAction( self.exitAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.listViewAction )
		self.viewMenuControl.addAction( self.textViewAction )
		
		self.textEdit = QtGui.QTextEdit()
		self.setCentralWidget( self.textEdit )
		
		
		
		### list Widget
		self.listWidget = QtGui.QWidget()
		self.listWidget.setWindowTitle( 'List' )
		self.listWidget.setStyleSheet('background: blue')
		self.listWidget.resize(250, 150)
		self.listWidget.move(550, 550)
		
		listWidgetLeft = QtGui.QWidget( self.listWidget )
		listWidgetLeft.setStyleSheet('background: black')
		layout = QtGui.QVBoxLayout( listWidgetLeft )
		layout.addStretch(  )
		listWidgetLeft.setLayout( layout )
		
		listWidgetRight = QtGui.QWidget( self.listWidget )
		listWidgetRight.setStyleSheet('background: white')
		layout = QtGui.QVBoxLayout( listWidgetRight )
		layout.addStretch(  )
		listWidgetRight.setLayout( layout )
		
		listWidgetSplitter = QtGui.QSplitter( QtCore.Qt.Horizontal, self.listWidget )
		listWidgetSplitter.addWidget( listWidgetLeft )
		listWidgetSplitter.addWidget( listWidgetRight )
		
		
		
		### text Widget
		self.textWidget = QtGui.QWidget()
		self.textWidget.setWindowTitle( 'Text' )
		self.textWidget.setStyleSheet('background: green')
		self.textWidget.resize(250, 150)
		self.textWidget.move(450, 450)
		
		textWidgetLeft = QtGui.QWidget( self.textWidget )
		textWidgetLeft.setStyleSheet('background: black')
		#layout = QtGui.QVBoxLayout( textWidgetLeft )
		#layout.addStretch( 1 )
		#textWidgetLeft.setLayout( layout )
		textWidgetLeftTextEdit = QtGui.QTextEdit( textWidgetLeft )
		textWidgetLeftTextEdit.setMaximumHeight( 1000 )
		
		textWidgetRight = QtGui.QWidget( self.textWidget )
		textWidgetRight.setStyleSheet('background: white')
		#layout = QtGui.QVBoxLayout( textWidgetRight )
		#layout.addStretch( 1 )
		#textWidgetRight.setLayout( layout )
		textWidgetRightTextEdit = QtGui.QTextEdit( textWidgetRight )
		textWidgetRightTextEdit.setMaximumHeight( 1000 )
		
		grid = QtGui.QGridLayout()
		grid.addWidget( textWidgetLeft, 0, 0 )
		grid.addWidget( textWidgetRight, 0, 1)
		self.textWidget.setLayout( grid )
		#textWidgetSplitter = QtGui.QSplitter( QtCore.Qt.Horizontal, self.textWidget )
		#textWidgetSplitter.addWidget( textWidgetLeft )
		#textWidgetSplitter.addWidget( textWidgetRight )
		
		
		
		### Show the MainWindow
		#self.listViewActionCallback()
		self.show()
	
	def listViewActionCallback( self ):
		self.listWidget.show()
	
	def textViewActionCallback( self ):
		self.textWidget.show()



def main():
	app = QtGui.QApplication( sys.argv )
	ui = SimpleMain()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
