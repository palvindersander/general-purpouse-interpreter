import argparse
import re
import os
import sys
from timeit import default_timer as timer
from enum import Enum
from scanner import scanner
from token import token
from expressions import *
from parser import parser
from interpreterRuntimeError import interpreterRuntimeError

paths = [".", "./lib"]
TokenType = Enum("TokenType", "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF")
TokenChar = {'(': "LEFT_PAREN", ')': "RIGHT_PAREN", '{': "LEFT_BRACE", '}': "RIGHT_BRACE", ',': "COMMA", '.': "DOT", '-': "MINUS", '+': "PLUS", ';': "SEMICOLON",
			 '*': "STAR", "!": "BANG", "!=": "BANG_EQUAL", "=": "EQUAL", "==": "EQUAL_EQUAL", "<": "LESS", "<=": "LESS_EQUAL", ">": "MORE", ">= ": "MORE_EQUAL", "/": "SLASH"}
Identifiers = {"and": "AND", "class": "CLASS", "else": "ELSE", "false": "FALSE", "for": "FOR", "fun": "FUN", "if": "IF", "nil": "NIL",
			   "or": "OR", "print": "PRINT", "return": "RETURN", "super": "SUPER", "this": "THIS", "true": "TRUE", "var": "VAR", "while": "WHILE"}

class interpreter:
	'''
	attrs: scanner, hadError
	'''

	hadError = False
	hadRuntimeError = False

	def __init__(self):
		# input arguments
		argParser = argparse.ArgumentParser(
			description="A basic interpreter for Pal, a general purpouse programming language")
		argParser.add_argument(
			"input", nargs=1, help="specify a input file containing a program to run")
		argParser.add_argument("-v", "--verbose", dest="verbose",
							action="store_true", help="show debugging output")
		self.args = argParser.parse_args()
		inputFilePath = self.args.input
		# run
		if inputFilePath != None:
			try:
				self.scanner = scanner(inputFilePath)
				if self.args.verbose:
					print(self.scanner.source)
				start = timer()
				self.run(inputFilePath)
				end = timer()
				if self.args.verbose:
					print("Execution finished in", (end-start), "seconds")
			except Exception as e:
				print(e)

	def run(self, inputFilePath):
		if interpreter.hadError or interpreter.hadRuntimeError:
			exit()
		tokens = self.scanner.scanTokens()
		for token in tokens:
			if self.args.verbose:
				print(token.toString())
		tokenParser = parser(tokens)
		expression = tokenParser.parse()
		if interpreter.hadError:
			return
		if self.args.verbose:
			print(expression.toString())
		self.interpret(expression)

	def interpret(self, expression):
		try:
			value = self.evaluate(expression)
			print(self.stringify(value))
		except interpreterRuntimeError as e:
			interpreter.runTimeError(e)

	def stringify(self, obj):
		if obj == None:
			return "nil"
		if type(obj) is float:
			text = str(obj)
			if len(text) > 2 and text[-2::] == ".0":
				text = text[0:-2]
			return text
		return str(obj)

	def visitLiteralExpr(self, expression):
		return expression.value

	def visitGroupingExpr(self, expression):
		return self.evaluate(expression.expression)

	def visitUnaryExpr(self, expression):
		right = self.evaluate(expression.right)
		if expression.op.type == "MINUS":
			self.checkNumberOperand(expression.op, right)
			return -1*float(right)
		elif expression.op.type == "BANG":
			return not self.isTruthy(right)
		return None

	def isTruthy(self, object):
		if object == None:
			return False
		elif type(object) is bool:
			return bool(object)
		return True

	def visitBinaryExpr(self, expression):
		left = self.evaluate(expression.left)
		right = self.evaluate(expression.right)
		if expression.op.type == "MINUS":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) - float(right)
		elif expression.op.type == "SLASH":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) / float(right)
		elif expression.op.type == "STAR":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) * float(right)
		elif expression.op.type == "PLUS":
			if type(left) is float and type(right) is float:
				return float(left) + float(right)
			elif type(left) is str and type(right) is str:
				return str(left) + str(right)
			raise interpreterRuntimeError(expression.op, "Operands must be two numbers or two strings.")
		elif expression.op.type == "GREATER":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) > float(right)
		elif expression.op.type == "GREATER_EQUAL":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) >= float(right)
		elif expression.op.type == "LESS":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) < float(right)
		elif expression.op.type == "LESS_EQUAL":
			self.checkNumberOperands(expression.op, left, right)
			return float(left) <= float(right)
		elif expression.op.type == "BANG_EQUAL":
			return not self.isEqual(left, right)
		elif expression.op.type == "EQUAL_EQUAL":
			return self.isEqual(left, right)
		return None

	def checkNumberOperand(self, op, operand):
		if type(operand) is float:
			return
		raise interpreterRuntimeError(op, "Operand must be a number.")

	def checkNumberOperands(self, op, left, right):
		if type(left) is float and type(right) is float:
			return
		raise interpreterRuntimeError(op, "Operands must be numbers")

	def isEqual(self, left, right):
		if left == None and right == None:
			return True
		if left == None:
			return False
		return left == right

	def evaluate(self, expression):
		if type(expression) is groupingExpr:
			return self.visitGroupingExpr(expression)
		elif type(expression) is literalExpr:
			return self.visitLiteralExpr(expression)
		elif type(expression) is binaryExpr:
			return self.visitBinaryExpr(expression)
		elif type(expression) is unaryExpr:
			return self.visitUnaryExpr(expression)

	@staticmethod
	def parseError(token,  message):
		if token.type == "EOF":
			interpreter.report(str(token.line), " at end", str(message))
		else:
			interpreter.report(str(token.line), " at '" + str(token.lexeme) + "'", str(message))

	@staticmethod
	def error(line, message):
		interpreter.report(line,"",message)

	@staticmethod
	def report(line, where, message):
		print("[line " + str(line) + "] Error" + str(where) + ": " + str(message))
		interpreter.hadError = True
	
	@staticmethod
	def runTimeError(error):
		print(str(error.message) + " [line " + str(error.token.line) + "]")
		interpreter.hadRuntimeError = True

interpreter()
