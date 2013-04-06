#!/usr/bin/python
# -*- conding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from unidecode import unidecode



class QHelper:
	UIInstance = None
	
	@classmethod
	def getValue( cls, widget ):
		if isinstance( widget, QtGui.QLineEdit ) or issubclass( widget.__class__, QtGui.QLineEdit ):
			return widget.text()
		elif isinstance( widget, QtGui.QComboBox ) or issubclass( widget.__class__, QtGui.QComboBox ):
			return widget.currentText()
		elif isinstance( widget, QtGui.QTextEdit ) or issubclass( widget.__class__, QtGui.QTextEdit ):
			return widget.toPlainText()
	
	@classmethod
	def master( cls, widget=None ):
		return cls.UIInstance
	
	@classmethod
	def str( cls, string ):
		if hasattr( string, 'toUtf8' ):
			string = str( string.toUtf8() ).decode( 'utf-8' )
		elif type( string ) == type( u' ' ):
			string = unidecode( string )
		elif not type( string ) == str:
			string = str( string )
		else:
			string = str( string )
		return string
