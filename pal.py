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


class parseError(RuntimeError):
	pass

class interpreterRuntimeError(RuntimeError):
	def __init__(self, token, message):
		self.message = message
		self.token = token

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
				interpreter.error(self.line, "Unexpected character.")

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
		self.addToken("NUMBER", float(self.source[self.start:self.current]))

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
			interpreter.error(self.line, "Unterminated string.")
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

	def toString(self):
		return "((" + self.left.toString() + "),(" + str(self.token.toString()) + "),(" + self.right.toString() + "))"


class unaryExpr(expr):
	'''
	attrs: op(token),right(expr)
	'''

	def __init__(self, op, right):
		self.token = self.op = op
		self.right = right

	def toString(self):
		return "((" + str(self.token.toString()) + "),(" + self.right.toString() + "))"


class literalExpr(expr):
	'''
	attrs: value(object)?
	'''

	def __init__(self, value):
		self.value = value

	def toString(self):
		return "(" + str(self.value) + ")"


class groupingExpr(expr):
	'''
	attrs: expression(expr)
	'''

	def __init__(self, expression):
		self.expression = expression
	
	def toString(self):
		return "(" + self.expression.toString() + ")"


class parser():
	'''
	attrs: tokens, current
	'''

	def __init__(self, tokens):
		self.tokens = tokens
		self.current = 0

	def parse(self):
		try:
			return self.expression()
		except parseError:
			return None

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
			return literalExpr(float(self.previous().literal))
		elif self.match(["STRING"]):
			return literalExpr(str(self.previous().literal))
		elif self.match(["LEFT_PAREN"]):
			expr = self.expression()
			self.consume("RIGHT_PAREN", "Expect ')' after expression.")
			return groupingExpr(expr)
		raise self.error(self.peek(), "Expect expression.")

	def error(self, peek, message):
		interpreter.parseError(peek, message)
		return parseError()

	def consume(self, type, message):
		if self.check(type):
			return self.advance()
		raise self.error(self.peek(), message)

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
