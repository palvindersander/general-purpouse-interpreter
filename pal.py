import argparse
import re
import os
import sys
from timeit import default_timer as timer
from enum import Enum

paths = [".", "./lib"]
TokenType = Enum("TokenType", "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF")
TokenChar = {'(': "LEFT_PAREN", ')': "RIGHT_PAREN", '{': "LEFT_BRACE", '}': "RIGHT_BRACE", ',': "COMMA", '.': "DOT", '-': "MINUS", '+': "PLUS", ';': "SEMICOLON", '*': "STAR", "!": "BANG", "!=" : "BANG_EQUAL", "=" : "EQUAL", "==" : "EQUAL_EQUAL", "<" : "LESS", "<=" : "LESS_EQUAL", ">" : "MORE", ">= " : "MORE_EQUAL", "/" : "SLASH"}
Identifiers = {"and" : "AND", "class" : "CLASS", "else" : "ELSE", "false" : "FALSE", "for" : "FOR", "fun" : "FUN", "if" : "IF", "nil" : "NIL", "or" : "OR", "print" : "PRINT", "return" : "RETURN", "super" : "SUPER", "this" : "THIS", "true" : "TRUE", "var" : "VAR", "while" : "WHILE"}

class scanner:
	'''
	attrs: source, tokens, start, current, line
	'''
	def __init__ (self, inputFilePath):
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
				interpreter.error(self.line, "", "Unexpected character.")

	def identifier(self):
		while self.peek().isalpha() or self.peek().isnumeric() or self.peek() == "_":
			self.current += 1
		string = self.source[self.start:self.current+1]
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
			interpreter.error(self.line, "", "Unterminated string.")
			return
		self.current += 1
		self.addToken("STRING", self.source[self.start+1:self.current-1])

	def addToken(self, type, literal):
		self.tokens.append(token(type,self.source[self.start:self.current],literal,self.line))

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
	attrs: type, lexeme, literal, line
	'''
	def __init__(self, type, lexeme, literal, line):
		self.type = type
		self.lexeme = lexeme
		self.literal = literal
		self.line = line

	def toString(self):
		return str(self.type) + " " + str(self.lexeme) + " " + str(self.literal);
		
class interpreter:
	'''
	attrs: scanner, hadError
	'''
	def __init__(self):
		# input arguments
		parser = argparse.ArgumentParser(description = "A basic interpreter for Pal, a general purpouse programming language")
		parser.add_argument("input", nargs = 1, help = "specify a input file containing a program to run")
		parser.add_argument("-v", "--verbose", dest = "verbose", action = "store_true", help = "show debugging output")
		args = parser.parse_args()
		inputFilePath = args.input
		# run
		if inputFilePath != None:
			try:
				self.scanner = scanner(inputFilePath)
				start = timer()
				self.run(inputFilePath)
				end = timer()
				if args.verbose:
					print(self.scanner.source)
					print("Execution finished in", (end-start), "seconds")
			except Exception as e:
				print(e)

	def run(self, inputFilePath):
		tokens = self.scanner.scanTokens()
		for token in tokens:
			print(token.toString())

	@staticmethod
	def error(line, where, message):
		print("[line " + str(line) + "] Error" + str(where) + ": " + str(message))
		#self.hadError = True
		exit()

interpreter()