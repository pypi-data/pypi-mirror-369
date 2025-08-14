import re
from typing import Union
from bson import ObjectId
from elemental_tools.Jarvis.tools.translation import Translation
from elemental_tools.logger import Logger
from elemental_tools.Jarvis.config import log_path
from elemental_tools.Jarvis.brainiac import NewRequest, Brainiac
from elemental_tools.Jarvis.tools import Tools

module_name = 'mercury'

logger = Logger(app_name='jarvis', owner='server', destination=log_path).log


class BasicServer:
	bypass_translator: bool = False
	_cache = []
	tools = Tools()
	examples_language: str = 'en'

	def translate_input(self, message: str, language: str):
		if not self.bypass_translator:
			try:
				logger('info', "Translating input information")

				# Identify text within double quotes using regular expressions
				double_quoted_texts = re.findall(r'"([^"]*)"', message)

				# Identify text within single quotes using regular expressions
				single_quoted_texts = re.findall(r"'([^']*)'", message)

				# Replace text within double quotes with a placeholder
				double_placeholder = 'DOUBLE_QUOTED_TEXT_PLACEHOLDER'
				message_without_double_quotes = re.sub(r'"([^"]*)"', f'"{double_placeholder}"', message)

				# Replace text within single quotes with a placeholder
				single_placeholder = 'SINGLE_QUOTED_TEXT_PLACEHOLDER'
				message_without_quotes = re.sub(r"'([^']*)'", f"'{single_placeholder}'", message_without_double_quotes)

				# Translate the modified message
				translated_message = Translation(source=language, target=self.examples_language).translate(message_without_quotes)

				# Replace the placeholders with the original text within quotes
				for double_quoted_text in double_quoted_texts:
					translated_message = translated_message.replace(f'"{double_placeholder}"',
																	f'"{double_quoted_text}"', 1)

				for single_quoted_text in single_quoted_texts:
					translated_message = translated_message.replace(f"'{single_placeholder}'",
																	f"'{single_quoted_text}'", 1)

				if translated_message.lower() != message.lower():
					logger('success', "The message was translated")
				else:
					logger('alert', "The message stays untranslated")

				result = translated_message

			except Exception as e:
				logger('error',f"Could not translate the message! Maybe some connection error, or something related to GoogleTranslator. Exception: {str(e)}")
				return None
				# raise Exception('Could not translate the message! Maybe some connection error, or something related to GoogleTranslator')

		else:
			result = message

		return result

	def translate_output(self, message: str, language: str):
		if not self.bypass_translator:
			try:
				logger('info', f"Translating output information: {message}")

				# Identify text within double quotes using regular expressions
				double_quoted_texts = re.findall(r'"([^"]*)"', message)

				# Identify text within single quotes using regular expressions
				single_quoted_texts = re.findall(r"'([^']*)'", message)

				# Replace text within double quotes with a placeholder
				double_placeholder = 'DOUBLE_QUOTED_TEXT_PLACEHOLDER'
				message_without_double_quotes = re.sub(r'"([^"]*)"', f'"{double_placeholder}"', message)

				# Replace text within single quotes with a placeholder
				single_placeholder = 'SINGLE_QUOTED_TEXT_PLACEHOLDER'
				message_without_quotes = re.sub(r"'([^']*)'", f"'{single_placeholder}'", message_without_double_quotes)

				# Translate the modified message
				translated_message = Translation(source=self.examples_language, target=language).translate(message_without_quotes)

				# Replace the placeholders with the original text within quotes
				for double_quoted_text in double_quoted_texts:
					translated_message = translated_message.replace(f'"{double_placeholder}"',
																	f'"{double_quoted_text}"', 1)

				for single_quoted_text in single_quoted_texts:
					translated_message = translated_message.replace(f"'{single_placeholder}'",
																	f"'{single_quoted_text}'", 1)

				if translated_message.lower() != message.lower():
					logger('success', "The outgoing message was translated")
				else:
					logger('alert', "The outgoing message stays untranslated")

				result = translated_message

			except Exception as e:
				logger('error',f"Could not translate the message! Maybe some connection error, or something related to GoogleTranslator. Exception: {str(e)}")

				return None
				#raise Exception(
				#	'Could not translate the message! Maybe some connection error, or something related to GoogleTranslator')

		else:
			result = message

		return result


class Server(BasicServer):

	def __init__(self, brainiac: Union[Brainiac, None] = None, bypass_translator: bool = False, adb: bool = False,
				 notifications_only: bool = False):
		"""Under construction"""
		from elemental_tools.api.controllers.user import UserController
        from elemental_tools.api.controllers.wpp import WppController
		from elemental_tools.api.controllers.notification import NotificationController

		self.wpp_db = WppController()
		self.notification_db = NotificationController()
		self.user_db = UserController()

	def get_lang_from_country_code(self, phone_number):
		log_owner = module_name + '-language-selector'
		self.tools.codes_and_languages()
		try:
			contact_lang = \
			[lang for code, lang in self.tools.codes_and_languages().items() if phone_number.startswith(code)][0]
		except:

			if phone_number.startswith('+'):
				contact_lang = 'en'
			else:
				contact_lang = 'auto'

		logger('info', f"The defined language is {contact_lang}")
		return contact_lang

	def verify_notifications(self):

		_to_send_notifications = {}
		_to_send_responses = {}

		_result_notifications = {}
		_result_responses = {}

		_is_there_notifications = self.notification_db.is_there_notifications()
		_is_there_responses = self.notification_db.is_there_responses()

		logger('info', f"Verifying for new Notifications...")

		# PREPARE NOTIFICATIONS
		if _is_there_notifications:
			logger('info', f"Notifications found!")
			_notifications = self.notification_db.query_all(self.notification_db.notification_selector)
		else:
			logger('alert', f"No Notifications found, skipping...")
			_notifications = []

		logger('info', f"Verifying for new Responses...")
		# PREPARE RESPONSES
		if _is_there_responses:
			logger('info', f"Responses found!")
			_responses = self.notification_db.query_all(self.notification_db.responses_selector)
		else:
			logger('alert', f"No Responses found, skipping...")
			_responses = []

		# ATTACH NOTIFICATIONS TO BE SENT
		for notification in _notifications:
			try:
				logger('info', f"Processing Notification {str(notification['_id'])}")

				if notification['sub'] is not None:
					_destination = self.user_db.query({'_id': ObjectId(notification['sub'])})

					_content = self.translate_output(notification['content'], _destination['language'])

					_to_send_notifications = {**_to_send_notifications, notification['_id']: {_destination['cellphone']: _content}}

				if notification['role'] is not None:

					_users_in_role = self.user_db.query_all({'role': {"$in": notification['role']}})

					for user in _users_in_role:
						_destination = self.user_db.query({'_id': ObjectId(user['_id'])})

						_content = self.translate_output(notification['content'], _destination['language'])

						_to_send_notifications[notification['_id']] = {_destination['cellphone']: _content}
			except:
				pass

		# ATTACH RESPONSES TO BE SENT
		for response in _responses:
			try:
				logger('info', f"Processing Response {str(response['_id'])}")

				if response['customer_id'] is not None:
					_destination = self.user_db.query({'_id': ObjectId(response['customer_id'])})

					_content = response['response']
					_to_send_responses = {**_to_send_responses, response['_id']: {_destination['cellphone']: _content}}

			except:
				pass

		# SEND NOTIFICATIONS
		for notification_id in _to_send_notifications:
			try:
				for destination, content in _to_send_notifications[notification_id].items():
					destination = destination
					content = content

					logger('info',
						f"Sending notification {str(notification_id)} to {str(destination)} and content {str(content)}")

					try:
						_request = NewRequest(
							message=content,
							cellphone=destination
						)

						_request.skill.result = content

						self.send_message(_request)

						_result_notifications[notification_id] = True

					except:
						_result_notifications[notification_id] = False
			except:
				pass

		# UPDATE THE NOTIFICATION DATABASE
		if _result_notifications.values() and _is_there_notifications:
			logger('info', f"Updating Notification Information")

			_update_notification_filter = []
			for notification_id in _result_notifications:
				if _result_notifications[notification_id]:
					_update_notification_filter.append(notification_id)

			_update_notification_result = self.notification_db.set_notifications_status(_update_notification_filter)

			if _is_there_notifications and all(_result_notifications.values()) and _update_notification_result:
				logger('success', f"Successfully sent notification's!")

			else:
				logger('error', f"Error sending some notification's, you should take a look.")

		# SEND RESPONSES
		for response_id in _to_send_responses:
			try:
				for destination, content in _to_send_responses[response_id].items():
					destination = destination
					content = content

					logger('info',
						   f"Sending Response {str(response_id)} to {str(destination)} and content: {str(content)}")

					try:
						_request = NewRequest(
							message=content,
							cellphone=destination
						)

						_request.skill.result = content

						_this_user = self.user_db.query({"cellphone": str(destination)})

						_selector_human_attendance_update = {"$and": [{"_id": ObjectId(_this_user["_id"])}, {
							"$or": [{"role": {"$exists": False}}, {"role": {"$nin": Constants.internal_roles}},
									{"admin": {"$ne": True}}]}]}

						_result_pipeline_under_human_attendance = self.user_db.update(_selector_human_attendance_update,
																					  {"is_human_attendance": True})

						self.send_message(_request)

						_result_responses[response_id] = True

					except:
						_result_responses[response_id] = False

			except:
				pass

		# UPDATE THE RESPONSES DATABASE
		if _result_responses.values() and _is_there_responses:
			logger('info', f"Updating Responses Information")

			_update_responses_filter = []

			for response_id in _result_responses:
				if _result_responses[response_id]:
					_update_responses_filter.append(response_id)

			_update_responses_result = self.notification_db.set_responses_status(_update_responses_filter)

			if _is_there_responses and all(_result_responses.values()) and _update_responses_result:
				logger('success', f"Successfully sent Responses!")

			else:
				logger('error', f"Error sending some Responses, you should take a look.")

		return _result_notifications, _result_responses

