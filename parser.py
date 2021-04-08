from parseError import parseError
from expressions import *

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
