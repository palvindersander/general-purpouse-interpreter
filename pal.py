import argparse
import re
import os
import sys
from timeit import default_timer as timer
from enum import Enum

paths = [".", "./lib"]
TokenType = Enum("TokenType", "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF")
TokenChar = {'(': "LEFT_PAREN", ')': "RIGHT_PAREN", '{': "LEFT_BRACE", '}': "RIGHT_BRACE", ',': "COMMA", '.': "DOT", '-': "MINUS", '+': "PLUS", ';': "SEMICOLON",
			 '*': "STAR", "!": "BANG", "!=": "BANG_EQUAL", "=": "EQUAL", "==": "EQUAL_EQUAL", "<": "LESS", "<=": "LESS_EQUAL", ">": "MORE", ">= ": "MORE_EQUAL", "/": "SLASH"}
Identifiers = {"and": "AND", "class": "CLASS", "else": "ELSE", "false": "FALSE", "for": "FOR", "fun": "FUN", "if": "IF", "nil": "NIL",
			   "or": "OR", "print": "PRINT", "return": "RETURN", "super": "SUPER", "this": "THIS", "true": "TRUE", "var": "VAR", "while": "WHILE"}


class scanner:
	'''
	attrs: source(string), tokens(token), start(int), current(int), line(int)
	'''

	def __init__(self, inputFilePath):
		self.source = ""
		self.read(inputFilePath)
		self.start = 0
		self.current = 0
		self.line = 0
		self.tokens = []

	def read(self, inputFilePath):
		path = inputFilePath[0]
		file = open(path)
		self.source = file.read()
		file.close()

	def scanTokens(self):
		while self.current < len(self.source):
			self.start = self.current
			self.scanToken()
		self.tokens.append(token("EOF", "", None, self.line))
		return self.tokens

	def scanToken(self):
		c = self.source[self.current]
		self.current += 1
		if c == " " or c == "\r" or c == "\t":
			return
		elif c == '"':
			self.string()
			return
		elif c == "\n":
			self.line += 1
			return
		elif c == "/":
			if self.match("/"):
				while self.peek() != "\n" and self.current < len(self.source):
					self.current += 1
			else:
				self.addToken(TokenChar[c], None)
			return
		elif self.match("=") and c+"=" in TokenChar:
			self.addToken(TokenChar[c+"="], None)
			return
		elif c in TokenChar:
			self.addToken(TokenChar[c], None)
			return
		elif c == "0":
			if self.match("o") == "r":
				self.addToken("OR", None)
				return
		else:
			if c.isnumeric():
				self.number()
				return
			elif c.isalpha() or c == "_":
				self.identifier()
				return
			else:
				interpreter.scannerError(self.line, "", "Unexpected character.")

	def identifier(self):
		while self.peek().isalpha() or self.peek().isnumeric() or self.peek() == "_":
			self.current += 1
		string = self.source[self.start:self.current]
		if string in Identifiers:
			self.addToken(Identifiers[string], None)
		else:
			self.addToken("IDENTIFIER", None)

	def number(self):
		while self.peek().isnumeric():
			self.current += 1
		if self.peek == "." and self.peekNext().isnumeric():
			self.current += 1
			while self.peek().isnumeric():
				self.current += 1
		self.addToken("NUMBER", int(self.source[self.start:self.current]))

	def peekNext(self):
		if self.current + 1 >= len(self.source):
			return "\0"
		return self.source[self.current+1]

	def string(self):
		while self.peek() != '"' and self.current < len(self.source):
			if self.peek() == "\n":
				self.line += 1
			self.current += 1
		if self.current >= len(self.source):
			interpreter.scannerError(self.line, "", "Unterminated string.")
			return
		self.current += 1
		self.addToken("STRING", self.source[self.start+1:self.current-1])

	def addToken(self, type, literal):
		self.tokens.append(
			token(type, self.source[self.start:self.current], literal, self.line))

	def match(self, c):
		if (self.current >= len(self.source)) or (self.source[self.current] != c):
			return False
		self.current += 1
		return True

	def peek(self):
		if self.current >= len(self.source):
			return "\0"
		return self.source[self.current]


class token:
	'''
	attrs: type(string), lexeme(string), literal(string), line(int)
	'''

	def __init__(self, type, lexeme, literal, line):
		self.type = type
		self.lexeme = lexeme
		self.literal = literal
		self.line = line

	def toString(self):
		return str(self.type) + " " + str(self.lexeme) + " " + str(self.literal)


class expr(object):
	pass


class binaryExpr(expr):
	'''
	attrs: left(expr),op(token),right(expr)
	'''

	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right


class unaryExpr(expr):
	'''
	attrs: op(token),right(expr)
	'''

	def __init__(self, op, right):
		self.token = self.op = op
		self.right = right


class literalExpr(expr):
	'''
	attrs: value(object)?
	'''

	def __init__(self, value):
		self.value = value


class groupingExpr(expr):
	'''
	attrs: expression(expr)
	'''

	def __init__(self, expression):
		self.expression = expression


class parser():
	'''
	attrs: tokens, current
	'''

	def __init__(self, tokens):
		self.tokens = tokens
		self.current = 0

	def parse(self):
		return self.expression()

	def expression(self):
		return self.equality()

	def equality(self):
		expr = self.comparison()
		while self.match(["BANG_EQUAL", "EQUAL_EQUAL"]):
			operator = self.previous()
			right = self.comparison()
			expr = binaryExpr(expr, operator, right)
		return expr

	def comparison(self):
		expr = self.term()
		while self.match(["GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"]):
			operator = self.previous()
			right = self.term()
			expr = binaryExpr(expr, operator, right)
		return expr

	def term(self):
		expr = self.factor()
		while self.match(["MINUS", "PLUS"]):
			operator = self.previous()
			right = self.factor()
			expr = binaryExpr(expr, operator, right)
		return expr

	def factor(self):
		expr = self.unary()
		while self.match(["SLASH", "STAR"]):
			operator = self.previous()
			right = self.unary()
			expr = binaryExpr(expr, operator, right)
		return expr

	def unary(self):
		if self.match(["BANG", "MINUS"]):
			operator = self.previous()
			right = self.unary()
			return unaryExpr(operator,right)
		return self.primary()

	def primary(self):
		if self.match(["FALSE"]):
			return literalExpr(False)
		elif self.match(["TRUE"]):
			return literalExpr(True)
		elif self.match(["NIL"]):
			return literalExpr(None)
		elif self.match(["NUMBER"]):
			return literalExpr(int(self.previous().literal))
		elif self.match(["STRING"]):
			return literalExpr(str(self.previous().literal))
		elif self.match(["LEFT_PAREN"]):
			expr = self.expression()
			self.consume("RIGHT_PAREN", "Expect ')' after expression.")
			return groupingExpr(expr)
		interpreter.parserError(self.peek(), "Expect expression.")

	def consume(self, type, message):
		if self.check(type):
			return self.advance()
		interpreter.parserError(self.peek(), message)

	def synchronize(self):
		self.advance()
		while not self.isAtEnd():
			if self.previous().type == "SEMICOLON":
				return
			elif self.peek().type in ["CLASS", "FUN", "VAR", "FOR", "IF", "WHILE", "PRINT", "RETURN"]:
				return
			self.advance()

	def match(self, types):
		for type in types:
			if self.check(type):
				self.advance()
				return True
		return False

	def check(self, type):
		if self.isAtEnd():
			return False
		return self.peek().type == type

	def advance(self):
		if not self.isAtEnd():
			self.current += 1
		return self.previous()

	def isAtEnd(self):
		return self.peek().type == "EOF"

	def peek(self):
		return self.tokens[self.current]

	def previous(self):
		return self.tokens[self.current-1]


class interpreter:
	'''
	attrs: scanner, hadError
	'''

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
				start = timer()
				self.run(inputFilePath)
				end = timer()
				if self.args.verbose:
					print(self.scanner.source)
					print("Execution finished in", (end-start), "seconds")
			except Exception as e:
				print(e)

	def run(self, inputFilePath):
		tokens = self.scanner.scanTokens()
		for token in tokens:
			if self.args.verbose:
				print(token.toString())
		tokenParser = parser(tokens)
		expression = tokenParser.parse()

	@staticmethod
	def scannerError(line, where, message):
		print("[line " + str(line) + "] Error" + str(where) + ": " + str(message))
		# self.hadError = True
		exit()

	@staticmethod
	def parserError(token, message):
		if token.type == "EOF":
			print("[line " + str(token.line) + "] Error" + " at end", str(message))
		else:
			print("[line " + str(token.line) + "] Error" + " at '" + str(token.lexeme) + "'", str(message))
		exit()


interpreter()
