class interpreterRuntimeError(RuntimeError):
	'''
	attrs: token, message
	'''
	def __init__(self, token, message):
		self.message = message
		self.token = token
