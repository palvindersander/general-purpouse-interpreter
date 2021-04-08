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
