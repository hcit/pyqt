#!/usr/bin/python
# -*- conding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from unidecode import unidecode



class QHelper:
	LOG_LEVEL_DEBUG = int( '0b0001', 2 )
	LOG_LEVEL_INFO = int( '0b0010', 2 )
	LOG_LEVEL_ERROR = int( '0b0100', 2 )
	UIInstance = None
	
	@classmethod
	def getValue( cls, widget ):
		if isinstance( widget, QtGui.QLineEdit ) or issubclass( widget.__class__, QtGui.QLineEdit ):
			value = widget.text()
		elif isinstance( widget, QtGui.QComboBox ) or issubclass( widget.__class__, QtGui.QComboBox ):
			value = widget.currentText()
		elif isinstance( widget, QtGui.QTextEdit ) or issubclass( widget.__class__, QtGui.QTextEdit ):
			value = widget.toPlainText()
		return cls.str( value )
	
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
	
	@classmethod
	def log( cls, *arg, **kwarg ):
		#print '--HELPER', arg
		if kwarg.get( 'LEVEL', cls.LOG_LEVEL_DEBUG ) == cls.LOG_LEVEL_DEBUG:
			pass
		else:
			print '::LOG', arg
