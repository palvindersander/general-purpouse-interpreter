import argparse
import os
import re
import sys
from enum import Enum
from timeit import default_timer as timer

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
		elif c == "o":
			if self.match("r"):
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


class statement(object):
	pass


class expressionStatement(statement):
	'''
	attrs: expression(expr)
	'''

	def __init__(self, expression):
		self.expression = expression

	def toString(self):
		return self.expression.toString()


class ifStatement(statement):
	'''
	attrs: condition(expr), thenBranch(statement), elseBranch(statement)
	'''

	def __init__(self, condition, thenBranch, elseBranch):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch
	
	def toString(self):
		return "if " + self.condition.toString()


class whileStatement(statement):
	'''
	attrs: condition(expr), body(statement)
	'''

	def __init__(self, condition, body):
		self.condition = condition
		self.body = body

	def toString(self):
		return "while " + self.condition.toString()


class printStatement(statement):
	'''
	attrs: expression(expr)
	'''

	def __init__(self, expression):
		self.expression = expression

	def toString(self):
		return "(print " + self.expression.toString() + ")"


class variableStatement(statement):
	'''
	attrs: name(token), initializer(expr)
	'''

	def __init__(self, name, initializer):
		self.initializer = initializer
		self.name = name

	def toString(self):
		return "(" + self.name.toString() + " " + self.initializer.toString() + ")"


class blockStatement(statement):
	'''
	attrs: statements(statement)
	'''

	def __init__(self, statements):
		self.statements = statements

	def toString(self):
		return str([statement.toString() for statement in self.statements])


class parser():
	'''
	attrs: tokens(token), current(int)
	'''

	def __init__(self, tokens):
		self.tokens = tokens
		self.current = 0

	def parse(self):
		statements = []
		while(not self.isAtEnd()):
			statements.append(self.declaration())
		return statements

	def declaration(self):
		try:
			if self.match(["VAR"]):
				return self.varDeclaration()
			return self.statement()
		except parseError as e:
			self.synchronize()
			return None

	def varDeclaration(self):
		name = self.consume("IDENTIFIER", "Expect variable name.")
		initializer = None
		if self.match(["EQUAL"]):
			initializer = self.expression()
		self.consume("SEMICOLON", "Expect ';' after variable declaration.")
		return variableStatement(name, initializer)

	def statement(self):
		if self.match(["FOR"]):
			return self.forStatement()
		elif self.match(["IF"]):
			return self.ifStatement()
		elif self.match(["PRINT"]):
			return self.printStatement()
		elif self.match(["WHILE"]):
			return self.whileStatement()
		elif self.match(["LEFT_BRACE"]):
			return blockStatement(self.block())
		return self.expressionStatement()

	def forStatement(self):
		self.consume("LEFT_PAREN", "Expect '(' after 'for'.")
		initializer = None
		if self.match(["SEMICOLON"]):
			initializer = None
		elif self.match(["VAR"]):
			initializer = self.varDeclaration()
		else:
			initializer = self.expressionStatement()
		condition = None
		if not self.check("SEMICOLON"):
			condition = self.expression()
		self.consume("SEMICOLON", "Expect ';' after loop condition.")
		increment = None
		if not self.check("RIGHT_PAREN"):
			increment = self.expression()
		self. consume("RIGHT_PAREN", "Expect ')' after for clauses.")
		body = self.statement()

		if increment != None:
			body = blockStatement([body,expressionStatement(increment)])
		if condition == None:
			condition = literalExpr(True)
		body = whileStatement(condition, body)
		if initializer != None:
			body = blockStatement([initializer, body])
		return body

	def whileStatement(self):
		self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
		condition = self.expression()
		self.consume("RIGHT_PAREN", "Expect ')' after condition.")
		body = self.statement()
		return whileStatement(condition, body)

	def block(self):
		statements = []
		while not self.check("RIGHT_BRACE") and not self.isAtEnd():
			statements.append(self.declaration())
		self.consume("RIGHT_BRACE", "Expect '}' after block.")
		return statements

	def ifStatement(self):
		self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
		condition = self.expression()
		self.consume("RIGHT_PAREN", "Expect ')' after if condition.")
		thenBranch = self.statement()
		elseBranch = None
		if self.match(["ELSE"]):
			elseBranch = self.statement()
		return ifStatement(condition, thenBranch, elseBranch)

	def printStatement(self):
		value = self.expression()
		self.consume("SEMICOLON", "Expect ';' after value.")
		return printStatement(value)

	def expressionStatement(self):
		expr = self.expression()
		self.consume("SEMICOLON", "Expect ';' after value.")
		return expressionStatement(expr)

	def parseSingle(self):
		try:
			return self.expression()
		except parseError:
			return None

	def expression(self):
		return self.assignment()

	def assignment(self):
		expr = self.lOr()
		if self.match(["EQUAL"]):
			equals = self.previous()
			value = self.assignment()
			if type(expr) is variableExpr:
				name = expr.name
				return assignExpr(name, value)
			self.error(equals, "Invalid assignment target.")
		return expr

	def lOr(self):
		expr = self.lAnd()
		while self.match(["OR"]):
			operator = self.previous()
			right = self.lAnd()
			expr = logicalExpr(expr, operator, right)
		return expr

	def lAnd(self):
		expr = self.equality()
		while self.match(["AND"]):
			operator = self.previous()
			right = self.equality()
			expr = logicalExpr(expr, operator, right)
		return expr

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
			return unaryExpr(operator, right)
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
		elif self.match(["IDENTIFIER"]):
			return variableExpr(self.previous())
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


class parseError(RuntimeError):
	pass


class interpreterRuntimeError(RuntimeError):
	'''
	attrs: token(token), message(string)
	'''

	def __init__(self, token, message):
		self.message = message
		self.token = token


class interpreter:
	'''
	attrs: scanner(scanner), hadError(bool), args(dict), enviroment(enviroment)
	'''

	hadError = False
	hadRuntimeError = False

	def __init__(self, args, scanner):
		self.args = args
		self.scanner = scanner
		self.enviroment = enviroment()

	def run(self):
		if interpreter.hadError or interpreter.hadRuntimeError:
			exit()
		tokens = self.scanner.scanTokens()
		for token in tokens:
			if self.args.verbose:
				print(token.toString())
		tokenParser = parser(tokens)
		statements = tokenParser.parse()
		if interpreter.hadError:
			return
		if self.args.verbose:
			print(statements)
		self.interpret(statements)

	def interpret(self, statements):
		try:
			for statement in statements:
				self.execute(statement)
		except interpreterRuntimeError as e:
			interpreter.runTimeError(e)

	def execute(self, statement):
		self.evaluate(statement)

	def stringify(self, obj):
		if obj == None:
			return "nil"
		if type(obj) is float:
			text = str(obj)
			if len(text) > 2 and text[-2::] == ".0":
				text = text[0:-2]
			return text
		return str(obj)

	def visitExpressionStatement(self, statement):
		self.evaluate(statement.expression)
		return None

	def visitBlockStatement(self, statement):
		self.executeBlock(statement.statements, enviroment(self.enviroment))
		return None

	def visitWhileStatement(self, statement):
		while self.isTruthy(self.evaluate(statement.condition)):
			self.execute(statement.body)
		return None

	def executeBlock(self, statements, enviroment):
		previous = self.enviroment
		try:
			self.enviroment = enviroment
			for statement in statements:
				self.execute(statement)
		finally:
			self.enviroment = previous

	def visitIfStatement(self, statement):
		if self.isTruthy(self.evaluate(statement.condition)):
			self.execute(statement.thenBranch)
		elif statement.elseBranch != None:
			self.execute(statement.elseBranch)
		return None

	def visitLogicalExpr(self, expression):
		left = self.evaluate(expression.left)
		if expression.op.type == "OR":
			if self.isTruthy(left):
				return left
		else:
			if not self.isTruthy(left):
				return left
		return self.evaluate(expression.right)

	def visitPrintStatement(self, statement):
		value = self.evaluate(statement.expression)
		print(self.stringify(value))
		return None

	def visitVarStatement(self, statement):
		value = None
		if statement.initializer != None:
			value = self.evaluate(statement.initializer)
		self.enviroment.define(statement.name.lexeme, value)
		return None

	def visitVariableExpr(self, expression):
		return self.enviroment.get(expression.name)

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

	def visitAssignExpr(self, expression):
		value = self.evaluate(expression.value)
		self.enviroment.assign(expression.name, value)
		return value

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
			raise interpreterRuntimeError(
				expression.op, "Operands must be two numbers or two strings.")
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

	def evaluate(self, obj):
		if type(obj) is groupingExpr:
			return self.visitGroupingExpr(obj)
		elif type(obj) is literalExpr:
			return self.visitLiteralExpr(obj)
		elif type(obj) is binaryExpr:
			return self.visitBinaryExpr(obj)
		elif type(obj) is unaryExpr:
			return self.visitUnaryExpr(obj)
		elif type(obj) is expressionStatement:
			return self.visitExpressionStatement(obj)
		elif type(obj) is printStatement:
			return self.visitPrintStatement(obj)
		elif type(obj) is variableExpr:
			return self.visitVariableExpr(obj)
		elif type(obj) is variableStatement:
			return self.visitVarStatement(obj)
		elif type(obj) is assignExpr:
			return self.visitAssignExpr(obj)
		elif type(obj) is blockStatement:
			return self.visitBlockStatement(obj)
		elif type(obj) is ifStatement:
			return self.visitIfStatement(obj)
		elif type(obj) is logicalExpr:
			return self.visitLogicalExpr(obj)
		elif type(obj) is whileStatement:
			return self.visitWhileStatement(obj)

	@staticmethod
	def parseError(token,  message):
		if token.type == "EOF":
			interpreter.report(str(token.line), " at end", str(message))
		else:
			interpreter.report(str(token.line), " at '" +
							   str(token.lexeme) + "'", str(message))

	@staticmethod
	def error(line, message):
		interpreter.report(line, "", message)

	@staticmethod
	def report(line, where, message):
		print("[line " + str(line) + "] Error" +
			  str(where) + ": " + str(message))
		interpreter.hadError = True

	@staticmethod
	def runTimeError(error):
		print(str(error.message) + " [line " + str(error.token.line) + "]")
		interpreter.hadRuntimeError = True


class expr(object):
	pass


class assignExpr(expr):
	'''
	attrs: name(token), value(expr)
	'''

	def __init__(self, name, value):
		self.name = name
		self.value = value

	def toString(self):
		return "(" + self.name.toString() + " " + self.value.toString() + ")"


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


class logicalExpr(expr):
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


class variableExpr(expr):
	'''
	attrs: name(token)
	'''

	def __init__(self, name):
		self.name = name

	def toString(self):
		return "(" + self.name.toString() + ")"


class enviroment():
	'''
	attrs: values(dict), enclosing(enviroment)
	'''

	def __init__(self, enclosing=None):
		self.values = {}
		if enclosing == None:
			self.enclosing = None
		else:
			self.enclosing = enclosing

	def define(self, name, value):
		self.values[str(name)] = value

	def get(self, name):
		if name.lexeme in self.values:
			return self.values[name.lexeme]
		if self.enclosing != None:
			return self.enclosing.get(name)
		raise interpreterRuntimeError(
			name, "Undefined variable '" + str(name.lexeme) + "'.")

	def assign(self, name, value):
		if name.lexeme in self.values:
			self.values[str(name.lexeme)] = value
			return
		if self.enclosing != None:
			self.enclosing.assign(name, value)
			return
		raise interpreterRuntimeError(
			name, "Undefined variable '" + str(name.lexeme) + "'.")


class pal():

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
				self.interpreter = interpreter(self.args, self.scanner)
				start = timer()
				self.interpreter.run()
				end = timer()
				if self.args.verbose:
					print("Execution finished in", (end-start), "seconds")
			except Exception as e:
				print(e)


if __name__ == "__main__":
	pal()
