import re


class Patterns:
	email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

	# Telephone Patterns
	phone_with_ddi = r'^\+\d{1,4}\s?\(\d{1,4}\)\s?\d{1,}$'
	phone_without_ddi = r'^\(\d{1,4}\)\s?\d{1,}$'
	phone_without_ddd = r'^\d{1,4}\s?\d{1,}$'

	# Zip Code Pattern (for Brazil, for example)
	zip_code = r'^\d{5}-\d{3}$'

	# CPF (Brazilian Individual Taxpayer Registry)
	cpf = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'

	# CNPJ (Brazilian National Legal Entities Registry)
	cnpj = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'

	# EIN (Employer Identification Number)
	ein = r'^\d{2}-\d{7}$'

	# Additional Pattern (example: some generic pattern)
	example_pattern = r'^[A-Za-z0-9]+$'

	@classmethod
	def validate_pattern(cls, pattern, value):
		"""
		Validates a value against a given pattern.

		Parameters:
		- pattern (str): Regular expression pattern.
		- value (str): Value to be validated.

		Returns:
		- bool: True if the value matches the pattern, False otherwise.
		"""
		return re.match(pattern, value) is not None