import gspread
from icecream import ic
from pydantic import BaseModel

from elemental_tools.scripts.google_synchronization.gsheet.config import google_credentials
import pandas as pd

gsheets = gspread.authorize(google_credentials)

create = gsheets.create
open = gsheets.open


def get_permissions(sheet):
	# Get the list of permissions for the sheet
	_permissions = gsheets.list_permissions(sheet.id)
	# Filter the list to get only editors' emails

	editor_emails = [permission['emailAddress'] for permission in _permissions if permission['role'] == 'writer']

	return editor_emails


class StatementDataframeAdjustment:

	dates: list = []
	institutions: list = []
	worksheets: list = []

	def __init__(self, df: pd.DataFrame):
		self.df = df

		self.apply_date_adjustment()

	def apply_date_adjustment(self):
		try:
			self.df['date'] = pd.to_datetime(self.df['date'], format='%d/%m/%Y %H:%M:%S')
		except:
			self.df['date'] = pd.to_datetime(self.df['date'], format="%Y-%m-%dT%H:%M:%S.%f")

	def return_dataframe(self):

		return self.df

