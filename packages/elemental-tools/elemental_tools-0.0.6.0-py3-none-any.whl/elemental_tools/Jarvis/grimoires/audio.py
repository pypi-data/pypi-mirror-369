import random

from icecream import ic

from elemental_tools.Jarvis import GrimoireClass, ExamplesModel, Argument
from elemental_tools.Jarvis.server.audio import AudioAssistant, AudioRequest, AudioAssistantConfig


def retrieve_language(text: str):
    for word in text.split(' '):
        if word in AudioAssistant.available_language_examples:
            return AudioAssistant.available_language[word]


class SetLanguage(GrimoireClass):
    examples = ExamplesModel(keywords=['language'], examples=['change language', 'set language', 'reset language'])

    def language(self, request=AudioRequest, language=Argument(desired_type=str, parser_function=retrieve_language, example_model=ExamplesModel(examples=AudioAssistant.available_language_examples), default=None)):
        possible_responses = ["No problem"]

        _config = AudioAssistantConfig()
        _config.language = language

        return str(random.choice(possible_responses))
