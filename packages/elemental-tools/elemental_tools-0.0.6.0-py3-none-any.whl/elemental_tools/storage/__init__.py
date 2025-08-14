class Cache:

	def __init__(self, file: str = cache_file):
		self.cache_file = file

		if not os.path.isdir(os.path.dirname(os.path.abspath(cache_file))):
			os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)

		self.cache_file_content = open(cache_file, 'a+')
		if self.cache_file_content.readlines():
			self.cache_file_content = self.load()
			try:
				data = eval(self.cache_file_content.read())
				for cache_item in data:
					for title, value in cache_item.items():
						setattr(self, title, value)

			except SyntaxError:
				raise Exception("Failed to parse the cache file!")

	def save(self):
		self.cache_file_content.write(
			str([{title: value for title, value in self.__dict__.items() if not title.startswith('__')}]))
		self.cache_file_content.close()
		return open(cache_file, 'a+')

	def load(self):
		return open(self.cache_file, 'a+')

	def get(self, prop):
		return getattr(self, prop, None)
