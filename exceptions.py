class InputError(Exception):
	pass

class ImportingError(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return "{}".format(self.message)