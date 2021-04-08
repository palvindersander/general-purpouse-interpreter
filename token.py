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
