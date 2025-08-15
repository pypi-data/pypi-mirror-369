import requests
from icecream import ic


class WhatsappOfficialAPI:

	def __init__(self, phone_id: str, token: str):

		self.phone_id = phone_id
		self.token = token
		self.messaging_product = "whatsapp"
		self.url = f'https://graph.facebook.com/v17.0/{self.phone_id}'
		self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": 'application/json'}

		self.health = requests.get(self.url, headers=self.headers)

		if self.health.status_code != 200:
			raise Exception(f'Failed to connect to {self.messaging_product.capitalize()} META API')

		self.health.result = self.health.json()
		self.health.phone_number = self.health.result['display_phone_number']
		self.health.code_verification_status = self.health.result['code_verification_status']

	def send_message(self, message, destination):
		destination = destination.replace('+', '')

		_data = {
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": destination,
			"type": "text",
			"text": {"body": message}
		}

		_result = requests.post(f"{self.url}/messages", headers=self.headers, json=_data)

		if _result.status_code != 200:
			raise Exception(f"Error sending message! Message from Server: {_result.text}")

		return _result

