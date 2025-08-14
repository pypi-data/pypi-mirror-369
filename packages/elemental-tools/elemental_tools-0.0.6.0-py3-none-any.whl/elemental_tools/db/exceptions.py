class InsertException(Exception):

	def __init__(self, _doc, *args, **kwargs):
		print(f"Cannot insert: {_doc}")


class Mismatch(Exception):
	def __init__(self, _doc, *args, **kwargs):
		print(f"Cannot find a document matching the selector: {_doc}")
