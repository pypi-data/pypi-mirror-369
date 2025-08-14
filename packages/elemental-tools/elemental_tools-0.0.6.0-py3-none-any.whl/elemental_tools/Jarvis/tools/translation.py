from deep_translator import GoogleTranslator


class Translation(GoogleTranslator):
    """
    @param source: source language to translate from
    @param target: target language to translate to
    """

    def __init__(self, *args, **kwargs):
        """
        @param source: source language to translate from
        @param target: target language to translate to
        """
        super().__init__(*args, **kwargs)
