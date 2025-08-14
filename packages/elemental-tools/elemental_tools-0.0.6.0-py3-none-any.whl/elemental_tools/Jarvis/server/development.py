from elemental_tools.logger import Logger
from elemental_tools.Jarvis.brainiac import Brainiac, NewRequest
from deep_translator import GoogleTranslator
from langdetect import detect_langs

from elemental_tools.Jarvis.exceptions import Error, Unauthorized, InvalidOption


# Author's commentary:
#
# This is the simplest default server available
# In this server we are able to understand the server functions
# To use the brainiac power, we must use the process_message method in order to process incoming messages, in these case, retrieved from the user input python built-in
# The method "brainiac.process_message" returns the result of the execution of the matching function, and could be used in conjunction with many other ideas, such as what the mercury server does.
# Be creative, and generate your own servers. Feel free to share them!
#
# Get inspired with these beautiful example:
#



class DevServer:

	def __init__(self, brainiac: Brainiac, debug: bool = False, bypass_translator: bool = False, bypass_language_adaptation: bool = False):
		# we load the brainiac in the function, with an argument
		self.logger = Logger(app_name='server', owner='development').log
		self.brainiac = brainiac

		self.bypass_translator = bypass_translator
		self.bypass_language_adaptation = bypass_language_adaptation

		# in order to keep the things working, we create a while loop
		while True:

			# here we are collecting the message, and generating a new request with it.
			# if we need, we can add some additional _request props here, such as user, and other stuff.
			_user_input = input('\nPlease type something to brainiac process:')

			processable_text = _user_input

			_language = detect_langs(processable_text)[0].lang

			if not self.bypass_translator:
				self.logger('info', f"The detected language is {_language}")
				try:
					self.logger('info', "Translating input information")
					processable_text = GoogleTranslator(source='auto', target='en').translate(
						_user_input.lower())

					if processable_text.lower() != _user_input.lower():
						self.logger('success', "The message was translated")
					else:
						self.logger('alert', "The message stays untranslated")

				except:
					pass

			_request = NewRequest(processable_text)
			_request.language = _language

			# in these case we are using a control variable, which indicates whenever the request must be processed inside or outside of this try/catch block
			if not debug:
				try:
					self.logger('success', f"\nRequest Output:\n {self.process_request(_request)}", owner='response')
				except (Error, Unauthorized, InvalidOption) as e:
					self.logger('error', f"\nException occurred while processing request:\n {str(e)}", owner='response')
			else:
				self.logger('success', f"\nRequest Output:\n {self.process_request(_request)}", owner='response')

	# finally our process_request function, that receive the previously generated _request in order to process_message with Brainiac
	def process_request(self, _request):
		result = self.brainiac.process_message(_request)

		processed_text = result

		if not self.bypass_translator:

			try:
				_to_lang = _request.language

				self.logger('info', f"Translating output from 'en' to {_to_lang}")
				processed_text = GoogleTranslator(source='en', target=_to_lang).translate(result)

				if processed_text.lower() != result.lower():
					self.logger('success', "The message was translated")
				else:
					self.logger('alert', "The message stays untranslated")

			except:
				pass

		return processed_text

# Remember that _request is different from request
# I'm not here to explain why. But...
# Please, have fun!
