import json
import os.path
import re
import random
import subprocess
from typing import Union

from icecream import ic

from elemental_tools.Jarvis import Brainiac, Grimoire, NewRequest, ExamplesModel, BrainiacRequest
from elemental_tools.Jarvis.server.basic import BasicServer

from elemental_tools.audio import AudioGenerator, AudioRecognition
from elemental_tools.logger import Logger
from elemental_tools.system import Config, run_cmd


class AudioAssistantConfig(Config):
    _path = os.path.join(os.path.abspath('.'), 'audio_assistant.config')
    language: str = 'en'

    def __init__(self, *target):
        super().__init__(*target)
        self._load()


class AudioRequest(BrainiacRequest):
    _config = AudioAssistantConfig()
    cellphone = None
    language: str = _config.language

    translated_message = None
    translated_message_model = None

    skill_examples = None

    def __init__(self, request):
        super().__init__()

        self.request = request

        for attr_name in dir(request):
            if not callable(getattr(request, attr_name)) and not attr_name.startswith("_"):
                setattr(self, attr_name, getattr(request, attr_name))

        for attr_name in dir(self._config):
            if not callable(getattr(self._config, attr_name)) and not attr_name.startswith("_"):
                setattr(self, attr_name, getattr(self._config, attr_name))

    def __call__(self):
        self._config._load()
        return self.request


class AudioAssistant(BasicServer):
    debug = True
    name = None
    _log = Logger(app_name="Elemental-Tools", owner='audio-assistant', origin='server', debug=debug).log

    voice_id = None
    input_device_id = None

    audio_generator = AudioGenerator()

    available_language: dict = {key.lower(): name for key, name in
                                audio_generator.available_languages.items()}
    available_language_examples: list = [lang_title.lower() for lang_title in
                                              list(available_language.keys())] + [
                                                 lang_title.lower() for lang_title in
                                                 list(available_language.values())]

    def __init__(self,
                 brainiac: Brainiac,
                 bypass_translator: bool = False,
                 language_grimoire: str = 'en',
                 language_response: str = 'en',
                 ):
        self.language = language_response

        self.brainiac = brainiac
        self.examples_language = language_grimoire
        self.bypass_translator = bypass_translator

        self.audio_recognizer = AudioRecognition(input_device_id=self.input_device_id, assistant_name=self.name)
        self.audio_recognizer.language = language_response
        self.audio_generator.language = language_response

        self.config = AudioAssistantConfig(self.audio_generator, self.audio_recognizer, self)
        self.language = self.config.language

    def process_new_request(self, message):

        if self.examples_language != self.language:
            message = self.translate_input(message, re.sub(r'-.*', '', self.language))

        _brainiac_request = NewRequest(
            message=message
        )

        try:
            response = self.brainiac.process_message(_brainiac_request)
        except Exception as e:
            response = str(e)

        if self.examples_language != self.language:
            response = self.translate_output(response, re.sub(r'-.*', '', self.language))

        self.audio_generator.generate_audio_from_string(response)

    def start(self):

        try:
            self.select_voice()
            self.audio_recognizer.listen_mic(self.process_new_request, self.audio_generator.generate_audio_from_string)
        except KeyboardInterrupt:
            pass
        finally:
            self.config.input_device_id = self.audio_recognizer.input_device_id

    def select_voice(self):
        voices = self.audio_generator.voices

        _available_voices = {}
        _count = 0
        _choices = "ID - Name\n"

        for voice in voices:
            if re.sub(r'-.*', '', self.language) in str(voice.languages):
                _available_voices[_count] = voice.id
                _choices += f"{_count} - {voice.name}\n"
                _count += 1

        while self.config.voice_id is None:
            try:
                self.config.voice_id = int(input(f"\nPlease select a voice for the assistant:\n{_choices}"))
                self.audio_generator.voice_id = _available_voices[self.config.voice_id]
                self.config.voice_id = self.audio_generator.voice_id

            except ValueError or KeyError as e:
                print("Invalid number, please inform a valid one.")

        if isinstance(self.config.voice_id, str):
            self.audio_generator.voice_id = self.config.voice_id

        elif isinstance(self.config.voice_id, int):
            self.audio_generator.voice_id = _available_voices[self.config.voice_id]
            self.config.voice_id = self.audio_generator.voice_id

    def confirm(self, text):
        _message = f"Are you sure you want to set to: {text}?"
        self.process_new_request(_message)


run_cmd("pip install pyaudio")

