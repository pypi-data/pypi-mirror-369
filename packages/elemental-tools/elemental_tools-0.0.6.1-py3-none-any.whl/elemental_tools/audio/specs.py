import os.path

supported_formats = ['.ogg', '.wav', '.mp3']
available_languages = ['en', 'pt', 'es', 'ru', 'fr', 'de']


class AudioPath:

    _path: str = None
    ext: str

    def __init__(self, path_string):
        if any([path_string.lower().endswith(fmt) for fmt in supported_formats]):

            try:

                self._path = os.path.abspath(path_string)
                _, self.ext = os.path.splitext(self._path)
                self.ext = self.ext.lower()

            except Exception as e:
                raise Exception(f"Invalid path: {str(e)}")

    def __call__(self, *args, **kwargs):
        return self._path








