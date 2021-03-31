import argparse
import re
import os
import sys
from timeit import default_timer as timer
from enum import Enum

paths = [".", "./lib"]
hadError = False
SOURCE_LINES = ""
SOURCE_LEN = 0
TokenTypes = Enum("TokenTypes", "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF")
TokenChars = {'(': "LEFT_PAREN", ')': "RIGHT_PAREN", '{': "LEFT_BRACE", '}': "RIGHT_BRACE", ',': "COMMA", '.': "DOT", '-': "MINUS", '+': "PLUS", ';': "SEMICOLON", '*': "STAR",}

def error(line, message):
	report(line, "", message)

def report(line, where, message):
	print("[line " + line + "] Error" + where + ": " + message)
	hadError = True

def makeTokenDict(ttype, lexeme, literal, line):
	if literal == None:
		return {"type" : TokenTypes[ttype], "lexeme" : lexeme, "literal" : None, "line" : line}
	else:
		return {"type" : TokenTypes[ttype], "lexeme" : lexeme, "literal" : TokenTypes[literal], "line" : line}

def scanner():
	tokens = []
	start = 0
	current = 0
	line = 0
	while(current < SOURCE_LEN):
		start = current
		if SOURCE_LINES[current] in TokenChars:
			tokens.append(makeTokenDict(TokenChars[SOURCE_LINES[current]], SOURCE_LINES[start:current+1], None, line))
		else:
			error(line, "Unexpected character.")
		current = current + 1
	tokens.append(makeTokenDict("EOF", "", None, line))
	return tokens

parser = argparse.ArgumentParser(description = "A basic interpreter for Pal, a general purpouse programming language")
parser.add_argument("input", nargs = 1, help = "specify a input file containing a program to run")
parser.add_argument("-v", "--verbose", dest = "verbose", action = "store_true", help = "show debugging output")
args = parser.parse_args()
inputFilePath = args.input

if inputFilePath != None:
	try:
		source = inputFilePath[0]
		file = open(source)
		SOURCE_LINES = file.read()
		SOURCE_LEN = len(SOURCE_LINES)
		file.close()
		start = timer()
		scanner()
		end = timer()
		if args.verbose:
			print(SOURCE_LINES)
			print(SOURCE_LEN)
			print("Execution finished in", (end-start), "seconds")
	except Exception as e:
		print(e)