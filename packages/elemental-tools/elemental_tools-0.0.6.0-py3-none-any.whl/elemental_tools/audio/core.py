import multiprocessing
import multiprocessing
import os
import tempfile
import uuid
from typing import Union

import pyttsx3
import speech_recognition as sr
from gtts import gTTS
from gtts.langs import _main_langs
from playsound import playsound
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.playback import play
from pyttsx3.voice import Voice
from speech_recognition import UnknownValueError, WaitTimeoutError, RequestError

from elemental_tools.audio.specs import AudioPath, available_languages
from elemental_tools.logger import Logger

_log = Logger(app_name="Elemental-Tools", owner='audio', origin='core').log


def _device_monitor_subprocess(audio_recognizer, _callback):
    while True:
        if audio_recognizer.list_mic() != audio_recognizer.available_input_devices and audio_recognizer.input_device_id is not None:
            audio_recognizer.available_input_devices = audio_recognizer.list_mic()
            _log('info', 'New input device found')
            _callback()


class AudioGenerator:
    """

    Methods
        - generate_audio_from_string: Generate a sound and play, from a string;
    """

    language: str = 'en'
    _temp_destination = os.path.join(tempfile.mkdtemp(prefix='etools_', suffix='_audio'), '_audio')
    output_device = None
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voices.append(Voice("_google", 'Google', languages=_main_langs().keys()))
    voice_id = None
    _languages = {
        'af': 'Afrikaans',
        'ar': 'Arabic',
        'bg': 'Bulgarian',
        'bn': 'Bengali',
        'bs': 'Bosnian',
        'ca': 'Catalan',
        'cs': 'Czech',
        'da': 'Danish',
        'de': 'German',
        'el': 'Greek',
        'en': 'English',
        'es': 'Spanish',
        'et': 'Estonian',
        'fi': 'Finnish',
        'fr': 'French',
        'gu': 'Gujarati',
        'hi': 'Hindi',
        'hr': 'Croatian',
        'hu': 'Hungarian',
        'id': 'Indonesian',
        'is': 'Icelandic',
        'it': 'Italian',
        'iw': 'Hebrew',
        'ja': 'Japanese',
        'jw': 'Javanese',
        'km': 'Khmer',
        'kn': 'Kannada',
        'ko': 'Korean',
        'la': 'Latin',
        'lv': 'Latvian',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'ms': 'Malay',
        'my': 'Myanmar (Burmese)',
        'ne': 'Nepali',
        'nl': 'Dutch',
        'no': 'Norwegian',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'pt-br': 'Brazilian Portuguese',
        'ro': 'Romanian',
        'ru': 'Russian',
        'si': 'Sinhala',
        'sk': 'Slovak',
        'sq': 'Albanian',
        'sr': 'Serbian',
        'su': 'Sundanese',
        'sv': 'Swedish',
        'sw': 'Swahili',
        'ta': 'Tamil',
        'te': 'Telugu',
        'th': 'Thai',
        'tl': 'Filipino',
        'tr': 'Turkish',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'vi': 'Vietnamese',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)'
    }
    available_languages = {name: value for name, value in zip(_languages.values(), _languages.keys())}

    def generate_audio_from_string(self, string, destination: str = _temp_destination):
        """

        Args:
            string: The text that you want to transform in audio
            destination: The path to store the generated audio in. It also can be None, if you don't need to save the output.

        Returns:
            Destination Path / None
        """
        if string != "" and string is not None:
            _log("info", f"Generating audio with {self.voice_id} from: {string}")

            if destination == self._temp_destination:

                if self.voice_id != "_google":
                    self.engine.setProperty('voice', self.voice_id)
                    self.engine.say(string)
                    self.engine.runAndWait()
                else:
                    _filename = os.path.join(self._temp_destination)

                    gTTS(string, lang=self.language).save(_filename)
                    playsound(_filename)
                    os.remove(_filename)
                return None
            else:
                self.engine.save_to_file(string, destination)
                return destination
        else:
            return None


class AudioRecognition:
    debug: bool = True
    keyword: Union[str, None] = None
    path: AudioPath
    audio_content: AudioSegment.from_file
    recognizer = sr.Recognizer()

    default_language: str = None
    language: str = 'en'
    input_device_id = None
    available_input_devices = []

    _checking_new_devices: bool = False

    def __init__(self, path: Union[AudioPath, None] = None, input_device_id: Union[int, None] = None, keyword: Union[str, None] = None, assistant_name: Union[str, None] = None):
        """
        Audio Recognizer that accepts audio files or listen to the input device.

        Args:

            path: - type: AudioPath or None;
                - When not set, the AudioRecognition will start using the input device instead of a file.

        """
        self.input_device_id = input_device_id
        self.keyword = keyword
        self.name = assistant_name
        if path is not None:
            self.path = path

            self.audio_content = AudioSegment.from_file(path())

            if self.path.ext != "wav":
                _temp_wav_path = tempfile.mkdtemp(prefix='etools_')
                _temp_wav_name = os.path.join(_temp_wav_path, f"{uuid.uuid4()}.wav")
                self.audio_content.export(_temp_wav_name, format="wav")
                self.path = AudioPath(_temp_wav_name)

            self.audio_content = normalize(self.audio_content, headroom=1)

    def play(self):
        """Play the audio content on the recognizer"""
        play(self.audio_content)

    def to_string(self, language=default_language):
        """
        Convert audio to string;

        Args:
            language: The language that will be used on the recognition;

        Returns:
            The content of the audio transcribed;
        """

        _possible_languages = available_languages.copy()

        with sr.AudioFile(self.path()) as source:
            _audio = self.recognizer.record(source)  # read the entire audio file

            while _possible_languages:

                try:
                    if self.debug:
                        _log('info', f'Attempting Audio Recognition on File: {self.path()}')

                    if language is not None:
                        _selected_lang = language

                    else:
                        _selected_lang = _possible_languages[0]

                    self.as_string = self.recognizer.recognize_google(_audio, language=_selected_lang)

                    _possible_languages = []

                    if self.debug:
                        _log('success', f'Audio Recognized with Language: {_selected_lang}')

                except UnknownValueError:
                    self.as_string = None

                if len(_possible_languages):
                    del _possible_languages[0]

            return self.as_string

    def _check_device_changes(self):
        """
        Verify if there's changes on the devices list;

        Args:
            callback: A function that will be executed whenever changes are gathered;

        Returns:
            Nothing, it will never brake.
        """

        if not self._checking_new_devices:
            process = multiprocessing.Process(target=_device_monitor_subprocess, args=(self, self._prompt_input_devices))
            process.start()

    @staticmethod
    def list_mic():
        """List available input devices"""
        return sr.Microphone.list_microphone_names()

    def _prompt_input_devices(self):
        """
        Generate the menu of the device selection;

        Returns:
            _menu (str): A message with the devices ID's, asking user to select a device;
        """
        available_input_devices = self.list_mic()
        count = 0
        _menu = "\nPlease select the id of the recording device you want to use:\n\n"
        _menu += 'ID - Name\n'
        for e in available_input_devices:
            _menu += f"{count} - {str(e)}\n"
            count += 1
        _menu += "Enter the ID of the input device you want to select:\n"

        return _menu

    def select_mic(self, device_id: Union[int, None] = None):
        """

        Args:
            device_id: The ID of the input device you want to select, if none is provided, it will prompt for device ID selection;

        Returns:
             device_id: The ID of the input device;
        """

        if device_id is None:
            while self.input_device_id is None:
                self.available_input_devices = self.list_mic()

                if len(self.available_input_devices):
                    try:
                        selected_id = int(input(self._prompt_input_devices()))

                        if len(self.available_input_devices) > selected_id and selected_id:
                            self.input_device_id = selected_id

                    except Exception as e:
                        print(str(e))

        return self.input_device_id

    def callback_audio(self, recognizer, audio):
        try:
            if self.debug:
                _log('info', f'Recognizing mic input...')
                if self.language:
                    _log('info', f'Applying language: {self.language}')
            text = self.recognizer.recognize_google(audio, language=self.language)
            if self.debug:
                _log('success', f'Mic input recognized!')
        except RequestError or UnknownValueError as e:
            if self.exception is not None:
                try:
                    self.exception(str(e))
                    if self.debug:
                        _log('alert', f'Failed to recognize: {str(e)}')
                except:
                    pass
            return None
        if text is not None:
            if self.debug:
                _log('success', f'Audio transcribed: {text}')
                _log('info', f'Calling the callback function: {str(self.callback)}')
            if self.keyword is None:
                self.callback(text)
            elif self.keyword in text or self.name.lower() in text.lower():
                self.callback(text)

    def listen_mic(self, callback: callable, exception: Union[callable, None] = None):
        """

        Args:
            callback (callable): The function that will be executed in a success scenario;
            exception (callable): The function that will be executed in a failure scenario;

        Returns:
            Never breaks!
            We Hope So...
        """
        self.callback = callback
        self.exception = exception

        if self.input_device_id is None:
            self.select_mic()

        mic = sr.Microphone(device_index=self.input_device_id)

        while True:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 1
                with mic as _source:
                    _log('info', f'Listening mic input...')
                    self.recognizer.adjust_for_ambient_noise(_source, 0.5)
                    try:
                        audio = self.recognizer.listen(_source, phrase_time_limit=20, timeout=10)
                    except WaitTimeoutError:
                        continue
                self.callback_audio(self.recognizer, audio)

            except AttributeError as e:

                if not "object has no attribute 'close'" in str(e):
                    _log("alert", f"Invalid Device, please try another one. Error: {str(e)}")
                    self.input_device_id = None

                self.listen_mic(callback, exception)

