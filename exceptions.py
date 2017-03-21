class InputError(Exception):
	pass

class RestingRateError(Exception):
	def __init__(self, message):
		self.message = message