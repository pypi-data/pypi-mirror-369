from time import sleep

from bson import ObjectId

from elemental_tools.config import root_user
from elemental_tools.logger import Logger

from elemental_tools.Jarvis.brainiac import NewRequest
from elemental_tools.Jarvis.brainiac import Brainiac

from elemental_tools.Jarvis.exceptions import Unauthorized, InvalidOption, Error

from elemental_tools.Jarvis.server.basic import Server
from elemental_tools.Jarvis.server.whatsapp.api import WhatsappOfficialAPI

from elemental_tools.api.models import UserRequestModel

from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.controllers.notification import NotificationController

from elemental_tools.api.controllers.wpp import WppController

from elemental_tools.config import log_path
from elemental_tools.Jarvis.config import webhook_db_url
from elemental_tools.Jarvis.tools import Tools, extract_and_remove_quoted_content
from elemental_tools.api.settings import SettingsController

module_name = 'wpp-official-server'


class WhatsappOfficialServer(Server):
	logger = Logger(app_name='jarvis', owner=module_name, destination=log_path).log

	wpp_db = WppController()
	notification_db = NotificationController()
	user_db = UserController()
	settings_db = SettingsController()

	if webhook_db_url is not None:
		from elemental_tools.api.controllers.webhook import WebhookController
		webhook_db = WebhookController()

	_cache = []
	tools = Tools()

	def __init__(self, brainiac: Brainiac, phone_number_id: str, token_wpp_api: str, timeout: float, bypass_translator: bool = False):

		self.timeout = timeout

		self.bypass_translator = bypass_translator

		self.brainiac = brainiac
		self.brainiac.bypass_translator = bypass_translator

		self.logger('info', f'Health Checking Wpp Official Server...')

		try:
			self.wpp_api = WhatsappOfficialAPI(phone_number_id, token_wpp_api)
			self.logger('success', f'Wpp Official API is up and running!')
		except:
			error_message = f'Unable to connect to Whatsapp official server, check your .env file or compose.\nMake sure to configure WPP_PHONE_NUMBER_ID and the WPP_API_TOKEN env variables.'
			self.logger('critical-error', error_message)
			raise Exception(error_message)

		self.logger('info', f'Whatsapp phone connected is {self.wpp_api.health.phone_number}')
		self.logger('alert', f'Whatsapp code verification status is: {self.wpp_api.health.code_verification_status}')

		self.logger('info', f'Checking Webhook Database...')
		new_messages = self.webhook_db.get_unprocessed_wpp_messages()

		self._start()

	def send_message(self, request: NewRequest):
		destination_phone, message = request.cellphone, request.skill.result

		_header = self.settings_db.get(root_user, "attendant_default_response_header")
		if _header is None:
			_header = self.settings_db.get(root_user, "company_name")

		message = f"*{_header}*\n\n{message}"

		self.logger('info', f'Sending Message Destination: {str(destination_phone)} Message: {str(message)}')
		self.wpp_api.send_message(destination=destination_phone, message=str(message))
		self.logger('success', f"Message has been sent!")

	def _start(self, timeout=5):
		self.logger('start', f"Initializing Whatsapp Official Server with Brainiac!")

		while True:
			self.logger('info', f"Checking for new messages on your webhook...")
			new_messages = self.webhook_db.get_unprocessed_wpp_messages()
			_gen_list = list(new_messages)
			if len(_gen_list[0]):
				self.logger('info', f"New messages found! Processing...")

				for current_index, incoming_message in enumerate(_gen_list):
					for message in incoming_message:
						user_ids = message.get('user_ids', [])
						messages = message.get('messages', [])

						for user_id, current_message in zip(user_ids, messages):
							wpp_user_id = user_id
							not_processed_id = current_message['id']
							incoming_phone = current_message['from']
							message_content = current_message['text']['body']

							_doc = {'msg_id': not_processed_id, 'cellphone': str(incoming_phone), 'wpp_user_id': str(wpp_user_id)}

							if self.wpp_db.add(_doc):
								self.logger('info', f'Processing message: id {not_processed_id}, contact {incoming_phone}, message {message_content}')
								user = self.user_db.query(selector={"wpp_user_id": wpp_user_id})

								if user is None:
									user = UserRequestModel()
									user.language = self.get_lang_from_country_code(incoming_phone)
									user.cellphone = incoming_phone
									user.wpp_user_id = str(wpp_user_id)
									_user_dict = user.model_dump()
									user.id = str(self.user_db.add(_user_dict)['_id'])
								else:
									user["id"] = user["_id"]
									user = UserRequestModel(**user)

								processable_text = self.translate_input(message=message_content, language=user.language)

								try:
									processable_text, quoted_content = extract_and_remove_quoted_content(processable_text)
								except:
									quoted_content = []

								if user.is_human_attendance:

									try:

										_pipeline_attendant_waiting_for_response = [
											{
												'$match': {"$and": [{"customer_id": user.get_id()},
																	{"responser_id": {'$exists': True}}]}
											},
											{
												'$sort': {
													'creation_date': 1
												}
											}
										]

										_agg = self.notification_db.collection.aggregate(_pipeline_attendant_waiting_for_response)

										_current_protocol = next(_agg)

										_current_attendant = self.user_db.query(
											{"_id": ObjectId(_current_protocol['responser_id'])})

										_attendant_request = NewRequest(
											message='',
											cellphone=_current_attendant['cellphone'],
											wpp_user_id=wpp_user_id
										)

										_requester_title = incoming_phone

										if user.name is not None:
											_requester_title += f" - {user.name}"

										_attendant_request_content = f"Protocol: \n{str(_current_protocol['_id'])}\n[{_requester_title}] "
										
										_attendant_request_content += f"{message_content}"
										
										_attendant_request.skill.result = _attendant_request_content
										
										self.send_message(_attendant_request)

									except:
										
										self.user_db.update({"_id": ObjectId(user.id)}, {"is_human_attendance": False})
										user.is_human_attendance = False

								if not user.is_human_attendance:

									_brainiac_request = NewRequest(
										message=processable_text,
										cellphone=incoming_phone,
										wpp_user_id=wpp_user_id,
										user=user
									)

									_brainiac_request.quoted_content = quoted_content
									_brainiac_request.last_subject = user.last_subject

									try:
										_brainiac_request.skill.result = self.brainiac.process_message(
											_brainiac_request
										)

									except Unauthorized as er:

										print("Raised Unauthorized")

										_brainiac_request.skill.result = str(er)

									except (InvalidOption, Error) as er:

										print("Raised InvalidOption")

										if user.last_subject and user.last_subject is not None:
											processable_text += f"\n{str(user.last_subject)}"

											_brainiac_request = NewRequest(
												message=processable_text,
												cellphone=incoming_phone,
												user=user,
												quoted_content=quoted_content
											)

											_brainiac_request.skill.result = self.brainiac.process_message(
												_brainiac_request
											)

										else:
											_brainiac_request.skill.result = str(er)

									_brainiac_request.skill.result = self.translate_output(_brainiac_request.skill.result, user.language)
									self.send_message(_brainiac_request)

					self.webhook_db.remove(incoming_message[current_index]['_id'])

			else:
				self.logger('alert', f"No new messages, skipping...")

			self.verify_notifications()
			sleep(self.timeout)

