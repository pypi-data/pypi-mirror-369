from datetime import datetime
from time import sleep
from typing import List

import gspread_dataframe as gd
import pandas as pd
from bson import ObjectId
from deep_translator import GoogleTranslator
from gspread import WorksheetNotFound
from gspread.utils import rowcol_to_a1
from gspread_formatting import *

from elemental_tools.api import constants as Constants
from elemental_tools.api.controllers.institution import InstitutionController
from elemental_tools.api.controllers.notification import NotificationController
from elemental_tools.api.controllers.statement import StatementController
from elemental_tools.api.controllers.transaction import TransactionController
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.models import UserRequestModel, GoogleDriveFolder, GooglePermission, GoogleSheet, \
    InstitutionRequestModel
from elemental_tools.api.models.notification import NotificationRequestModel
from elemental_tools.api.settings import SettingsController
from elemental_tools.logger import Logger
from elemental_tools.scripts.google_synchronization import gdrive
from elemental_tools.scripts.google_synchronization.gsheet import gsheets, get_permissions, StatementDataframeAdjustment

logger = Logger(app_name='google-sync', owner='synchronization').log

settings = SettingsController()
google_sheet_users_root_folder_id = settings.get('root', f'google_sheet_users_root_folder_id')


class StatementSettings:
    excluded_columns = ['_id', 'status', 'sub', 'type']
    translated_columns = ['date', 'name', 'value', 'institution', 'quotation', 'closures']
    skip_cols = 1
    start_row = 1 + skip_cols


class TransactionSettings:
    excluded_columns = ['status', 'sub', 'type', 'creation_date', 'currency_from', 'currency_to']
    rename_columns = {'_id': 'id', 'amount_from': 'cost', 'price': 'quotation', 'amount_to': 'USDT'}
    translated_columns = ['date', 'name', 'value', 'institution', 'quotation', 'closures']
    to_send = ['_id', 'date', 'amount_from', 'price', 'amount_to']
    skip_cols = 1
    start_row = 1 + skip_cols


class GoogleSync:
    app_name = 'google-sync'
    dashboard_title = 'Dashboard'
    _already_send = False

    user_db = UserController()

    institution_db = InstitutionController()
    _settings = SettingsController()
    transaction_db = TransactionController()

    _default_google_folders = [
        'statement'
    ]
    _default_sheet_name = 'Control'
    _default_statement_columns = ['date', 'description', 'value', 'obs']
    _default_statement_columns_colors = [None, '#f7e59c', '#98d0dd', "#f5e4cd"]

    currency_format = {
        "numberFormat": {
            "type": "CURRENCY",
            "pattern": "R$ #,##0.00"
        }
    }

    _default_statement_columns_formatting = [None, currency_format, currency_format, None]

    _result = []
    _errors = []

    pending_permissions = {
        "user": {},
        "admin": []
    }

    def __init__(self, sub: str, timeout: float = 30.0):
        """
		Receive UID to Sync With Google Sheet and create the default or recreate whenever initialized.

		To send the statement to Google Sheet, use the sync_statement method, to send the transactions, use the sync_transaction method.

		:param sub: user identifier (bson id) as string
		:type sub: str
		"""
        self.timeout = timeout
        self.sub = sub

        # retrieve the user doc
        self._current_user = self._retrieve_user_model()
        self._current_user_selector = {'_id': {"$eq": self._current_user.get_id()}}

        # start the sync processes
        self.create_complete_structure()
        self.check_for_unset_permissions()

    def _retrieve_user_model(self):
        # retrieve the user doc
        _current_user = self.user_db.query(selector={'_id': ObjectId(self.sub)})
        if _current_user is not None:
            _current_user = UserRequestModel(**_current_user)
            return _current_user
        else:
            raise Exception('User not found!')

    def create_complete_structure(self):
        logger('info', f"Creating complete folder structure")
        _result = False
        _new_folders = {}

        # create the folder needed according to the required folder structure on _default_google_folders:
        if not len(self._current_user.get_google().drive) >= len(self._default_google_folders):
            for _default_drive_folder_caption in self._default_google_folders:
                _new_google_drive_folder = GoogleDriveFolder(folder_caption=_default_drive_folder_caption)
                try:
                    _folder_caption_translated_to_the_users_lang = str(
                        GoogleTranslator(source='en', target=self._current_user.language).translate(
                            _default_drive_folder_caption)).capitalize()
                    _folder_suffix = str(
                        GoogleTranslator(
                            source='en',
                            target=self._current_user.language)
                        .translate(
                            'Shared Folder'
                        )
                    ).capitalize()
                    _folder_name = f"""{_folder_caption_translated_to_the_users_lang} - """

                    if self._current_user.name is not None:
                        _folder_name += f"{str(self._current_user.name)} - "
                    else:
                        _folder_name += f"{str(self._current_user.cellphone)} - "

                    _folder_name += _folder_suffix

                    # create the folder and add the model to the user model
                    _new_google_drive_folder.external_id = gdrive.create_folder(_folder_name,
                                                                                google_sheet_users_root_folder_id)
                    self._current_user = self._retrieve_user_model()

                    # save a notification for the user
                    _notification_controller = NotificationController()

                    _new_protocol = NotificationRequestModel(sub='root')
                    _new_protocol.client_id = ObjectId(self._current_user.get_id())

                    url = f"{Constants.url_google_drive}{_new_google_drive_folder.external_id}"

                    _new_protocol.content = f"[Notification] New folder created!\n You can access it in a minute at: {url}\n{self._settings.get('root', 'attendant_default_response_request_attendance')}"

                    _protocol_add_result = _notification_controller.add(_new_protocol)

                    _update_content = {
                        f"google.drive.{_default_drive_folder_caption}.external_id": _new_google_drive_folder.external_id,
                        f"google.drive.{_default_drive_folder_caption}.folder_caption": _default_drive_folder_caption,
                        f"google.drive.{_default_drive_folder_caption}.permissions": []
                    }
                    logger('success', f"Folder created successfully!")
                    self.user_db.update(self._current_user_selector, _update_content)

                except Exception as e:
                    logger('critical-error', f"Failed to store a new GDrive Folder because of exception: {str(e)}")
                    self._errors.append(str(e))

            self._current_user = self._retrieve_user_model()

            _result = True

        return _result

    def check_folder(self, folder_name):
        _this_folder = self._current_user.get_google().drive.get(folder_name, None)

        if _this_folder is None:
            _create_structure_result = self.create_complete_structure()
            if _create_structure_result:
                return self._current_user.get_google().drive.get(folder_name).external_id

        else:
            return self._current_user.get_google().drive.get(folder_name).external_id

    def check_for_unset_permissions(self):
        logger('info', f"Checking for unset permissions")
        self._current_user = self._retrieve_user_model()

        _all_admins = list(self.user_db.query_all(
            {
                "$and": [
                    {'status': True},
                    {'email': {"$ne": None}}
                ]
            }
        ))
        logger('info', f"Checking for unset permissions found these admins: {str(_all_admins)}")
        # FOLDER SYNC
        #
        # for every folder in the Google user information
        for _folder_name, _folder in self._current_user.get_google().drive.items():

            _pending_admin_emails = []
            _permissions_currently_set = [_permission for _permission in _folder.permissions]

            # iterates through the admins for checking for new permissions to be set
            if _all_admins is not None:
                for _admin in _all_admins:

                    # append the admin email if it not in folder permissions
                    if _admin['email'] not in _permissions_currently_set:
                        _new_permission_to_be_set = {
                            "sub": str(_admin['_id']),
                            "email": _admin['email'],
                            "date": datetime.now().isoformat(),
                            "folder_id": _folder.external_id
                        }

                        _pending_admin_emails.append(_admin['email'])
                        _permissions_currently_set.append(_admin['email'])

                        # add the new permission to the permissions to be set list
                        self.pending_permissions['admin'].append(_new_permission_to_be_set)

            # iterates through the default admins retrieved from the settings section checking for new email permissions to be set
            for _default_permission_email in list(settings.get('root', f'google_sheet_default_permissions', [])):

                if _default_permission_email not in _permissions_currently_set:
                    _new_permission_to_be_set = {
                        "sub": 'root',
                        "email": _default_permission_email,
                        "date": datetime.now().isoformat()
                    }

                    _pending_admin_emails.append(_default_permission_email)
                    _permissions_currently_set.append(_default_permission_email)

                    # add the new permission to the permissions to be set list
                    self.pending_permissions['admin'].append(_new_permission_to_be_set)
        #
        # for every sheet in the Google user information
        _permissions_currently_set = self._current_user.get_google().sheets_permissions
        
        # if there's any pending permissions, retrieve admin email list and set the permissions for each folder
        _this_emails = []
        if len(self.pending_permissions['admin']):
            _email_list = []
            _permissions_set = []
            for admin in self.pending_permissions['admin']:
                _email_list.append(admin['email'])
            for _folder_name, _folder in self._current_user.get_google().drive.items():
                logger('info', f"Setting permissions for folder: {_folder_name} of external_id: {_folder.external_id}",
                       app_name=self.app_name)
                _list_of_set_permission_emails = gdrive.set_folder_permissions(folder_id=_folder.external_id,
                                                                               email_list=_email_list)
                _new_drive_permissions = List[GooglePermission]

                for _permission in self.pending_permissions['admin']:
                    for _email in _list_of_set_permission_emails:
                        if _permission['email'] == _email:
                            _this_emails.append(_email)
                            _complete_permissions = self._current_user.google.drive[_folder_name].permissions.append(
                                _email)

                self.user_db.update({"_id": self._current_user.get_id()},
                                    {f"google.drive.{_folder_name}.permissions": self._current_user.google.drive[
                                        _folder_name].permissions})

                logger('success', f"Permissions successfully updated for {_folder_name}!", app_name=self.app_name)

        # SHEET SYNC
        #
        # for every sheet in the Google user information

        for _sheet_name, _sheet in self._current_user.get_google().sheets.items():
            _pending_user_emails = []

            # save the sheet id and the email list that will be parsed to the request body
            self.pending_permissions['user'][_sheet.external_id] = _pending_user_emails

            if self._current_user.email not in _sheet.authorized_emails and self._current_user.email is not None and self._current_user.email not in _permissions_currently_set:
                _this_sheet = gsheets.open_by_key(_sheet.external_id)
                try:
                    logger('info', f"Setting permissions for sheet: {_sheet_name} of external_id: {_sheet.external_id}",
                           app_name=self.app_name)
                    _this_sheet.share([self._current_user.email], perm_type='user', role='writer')
                    _currently_auth_email_list = get_permissions(sheet=_this_sheet)
                    if len(_currently_auth_email_list):
                        _this_emails = + _currently_auth_email_list
                        self.user_db.update(self._current_user_selector,
                                            {
                                                f'google.sheets.{_sheet_name}.authorized_emails': _currently_auth_email_list,
                                                "google.sheets_permissions": _permissions_currently_set})
                    logger('success', f"Permissions successfully updated for {_sheet_name}!", app_name=self.app_name)
                except:
                    logger('error', f"Cannot updated permissions for {_sheet_name}!", app_name=self.app_name)
            elif self._current_user.email in _permissions_currently_set and self._current_user.email is not None:
                self.user_db.update(self._current_user_selector,
                                    {f'google.sheets.{_sheet_name}.authorized_emails': [self._current_user.email]})

            if self._current_user.email not in _permissions_currently_set:
                _pending_user_emails.append(self._current_user.email)
                _permissions_currently_set.append(self._current_user.email)

        self.user_db.update(self._current_user_selector,
                            {f'google.sheets_permissions': [self._current_user.email]})

    def get_available_pos_institution(self, statement_shape, institution_id):
        """
		:param statement_shape: The shape tuple obtained from np.array.shape
		:param institution_internal_label: Receives the label for the current institution, that must matches the one find in the sheet institution header.
		:return: _row, _col.
		"""
        try:
            _this_institution_data = InstitutionRequestModel(
                **self.institution_db.query({'_id': ObjectId(institution_id)}))

            _worksheet_inst_separator = self._current_worksheet.find(
                _this_institution_data.alias.upper(),
                in_row=1,
                case_sensitive=False
            )
            _row = None
            _col = _worksheet_inst_separator.col

        except:
            _col = 1 + StatementSettings().skip_cols

        class FirstEmptyCell:

            def __init__(self, row: int):
                self.row = row
                self.col = _col

        _row = None

        if self._current_worksheet.row_count == StatementSettings().start_row:
            _row = StatementSettings().start_row + 1
        else:
            _first_empty_cell = self._current_worksheet.find(r'', in_column=_col,
                                                             case_sensitive=False)
            if _first_empty_cell is None:
                _first_empty_cell = FirstEmptyCell(row=self._current_worksheet.row_count)

                self._current_worksheet.add_rows(1)
            if _first_empty_cell.col == _col:
                # check for each nearby cell in these row to avoid mixing statement information
                while _row is None:
                    for i in range(statement_shape[1]):
                        if self._current_worksheet.cell(row=_first_empty_cell.row,
                                                        col=_first_empty_cell.col + i).value is None:
                            _row = _first_empty_cell.row
                        else:
                            _first_empty_cell.row += 1

        return _row, _col

    def generate_sheet_title(self, month, year):
        sheet_title = f"{self._default_sheet_name} - "

        if self._current_user.name is not None:
            sheet_title += f"{str(self._current_user.name)} - "
        else:
            sheet_title += f"{str(self._current_user.cellphone)} - "

        sheet_title += f"{month}/{year}"

        return sheet_title

    def statement_to_sheet(self, df=None):

        def prepare_dataframe(_current_chunk):
            df = pd.DataFrame(_current_chunk)
            statement_settings = StatementSettings()
            _clean_df = df.drop(columns=statement_settings.excluded_columns, errors='ignore')

            _clean_df.drop(columns="institution", errors='ignore', inplace=True)

            _clean_df['value'] = _clean_df['value'].astype(str).str.replace('.', ',')

            _clean_df = _clean_df[['date', 'name', 'value']]

            for field in statement_settings.translated_columns:
                if field in _clean_df.columns:
                    _clean_df.rename(columns={field: str(
                        GoogleTranslator(source='en', target=self._current_user.language).translate(
                            field)).capitalize()},
                                     inplace=True)

            return _clean_df

        self._current_user = self._retrieve_user_model()

        c_year = datetime.now().strftime('%Y')
        c_month = datetime.now().strftime('%m')
        sheet_title = f"{self._default_sheet_name} - {self._current_user.name} {c_month}/{c_year}"
        _statement_alias = f"{c_year}/{c_month}"
        _user_folder_id = self._current_user.get_google().drive.get('statement', GoogleDriveFolder()).external_id

        _sheet = self.create_or_retrieve_sheet(sheet_title, c_year, c_month, _user_folder_id)

        dash_worksheet = self.generate_or_retrieve_new_dashboard(_sheet)

        if df is not None:

            df.dropna(subset=['institution_id'], inplace=True)

            unique_years = df['date'].dt.year.unique()
            for year in unique_years:

                this_year_months = df[df['date'].dt.year == year]

                unique_months = this_year_months['date'].dt.month.unique()

                for month in unique_months:
                    month = int(month)
                    sheet_title = self.generate_sheet_title(month, year)

                    _this_month_statement = df[
                        (df['date'].dt.month == month) & (
                                df['date'].dt.year == year)]

                    unique_days = _this_month_statement['date'].dt.day.unique()
                    for day in unique_days:

                        _current_statement_chunk = _this_month_statement[_this_month_statement['date'].dt.day == day]

                        worksheet_tab_name = f"{day}/{month}"

                        _sheet = self.create_or_retrieve_sheet(sheet_title, year, month, _user_folder_id)
                        self.statement_retrieve_or_create_worksheet_for_the_day(worksheet_tab_name=worksheet_tab_name,
                                                                                _user_folder_id=_user_folder_id,
                                                                                sheet=_sheet,
                                                                                _statement_alias=_statement_alias,
                                                                                skip_cols=StatementSettings().skip_cols)

                        _df_institutions = _current_statement_chunk['institution_id'].unique()

                        _inst_hip_index = 0

                        _initial_row_count = self._current_worksheet.row_count

                        for institution_id in _df_institutions:
                            _to_send_dataframe = _current_statement_chunk[
                                _current_statement_chunk['institution_id'] == institution_id]

                            
                            _to_send_dataframe.sort_values(by='date', ascending=True, inplace=True)
                            

                            _clean_data = prepare_dataframe(_to_send_dataframe)

                            _institution_available_pos = self.get_available_pos_institution(_clean_data.shape,
                                                                                            institution_id)
                            _row = _institution_available_pos[0]
                            _col = _institution_available_pos[1]

                            _statement_area_row_count = self._current_worksheet.row_count - _initial_row_count
                            _row_count_to_append = _clean_data.shape[0] - _statement_area_row_count
                            self._current_worksheet.insert_rows([[''] for _i in range(_row_count_to_append)], row=_row)
                            gd.set_with_dataframe(
                                worksheet=self._current_worksheet,
                                dataframe=_clean_data,
                                row=_row,
                                include_index=False,
                                include_column_header=False,
                                resize=False,
                                col=_col
                            )
                            StatementController(sub=_to_send_dataframe.sub.unique()[0]).update(
                                selector={"_id": {"$in": list(_to_send_dataframe['_id'].to_list())}},
                                content={"status": True})
                            _inst_hip_index += 1

                            self.dashboard_reload(sheet=_sheet, dash_worksheet=dash_worksheet)

                            sleep(self.timeout)

                        self._current_user = self._retrieve_user_model()

        else:

            worksheet_tab_name = datetime.now().strftime("%d/%m")
            self.statement_retrieve_or_create_worksheet_for_the_day(worksheet_tab_name=worksheet_tab_name,
                                                                    _user_folder_id=_user_folder_id, sheet=_sheet,
                                                                    _statement_alias=_statement_alias,
                                                                    skip_cols=StatementSettings().skip_cols)

        self.dashboard_reload(sheet=_sheet, dash_worksheet=dash_worksheet)

    def sync_statement(self):

        self._current_user = self._retrieve_user_model()

        statement_db = StatementController(sub=str(self._current_user.get_id()))

        _user_not_processed_statement = list(statement_db.retrieve_statement(_type='income', status=None))

        processed_statement_dataframe = None
        if len(_user_not_processed_statement):
            # Load the dataframe with the statement information
            _df = pd.DataFrame(_user_not_processed_statement)

            # Start a handler that deals with the default changes on the dataframe
            processed_statement_dataframe = StatementDataframeAdjustment(_df).return_dataframe()

            # send the retrieved statement to gsheets or create a new statement sheet for the current day
            result = self.statement_to_sheet(processed_statement_dataframe)

            return result

    def generate_or_retrieve_new_dashboard(self, sheet):
        try:
            _worksheet_dashboard = sheet.worksheet(self.dashboard_title)
        except WorksheetNotFound:

            _worksheet_dashboard = sheet.add_worksheet(self.dashboard_title, rows=6, cols=10)

            dashboard_format = {
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE"
            }

            currency_brl = {
                "numberFormat": {
                    "type": "CURRENCY",
                    "pattern": "R$ #,##0.00"
                }
            }

            currency_usdt = {
                "numberFormat": {
                    "type": "CURRENCY",
                    "pattern": "$ #,##0.000"
                }
            }

            _worksheet_dashboard.format(':', dashboard_format)

            # MERGE BALANCE CELLS
            _worksheet_dashboard.merge_cells(1, 1, 2, 2, merge_type='MERGE_ALL')
            _worksheet_dashboard.merge_cells(3, 1, 4, 2, merge_type='MERGE_ALL')

            _worksheet_dashboard.merge_cells(1, 3, 2, 4, merge_type='MERGE_ALL')
            _worksheet_dashboard.merge_cells(3, 3, 4, 4, merge_type='MERGE_ALL')

            _worksheet_dashboard.merge_cells(5, 1, 6, 4, merge_type='MERGE_ALL')

            # MERGE TRANSACTION CELLS
            #
            # Label
            _worksheet_dashboard.merge_cells(1, 6, 1, 10, merge_type='MERGE_ALL')
            # Cost
            _worksheet_dashboard.merge_cells(6, 7, 6, 8, merge_type='MERGE_ALL')
            # USDT Total
            _worksheet_dashboard.merge_cells(6, 9, 6, 10, merge_type='MERGE_ALL')

            # SET VALUES
            #
            # Title's
            _range_titles = _worksheet_dashboard.range('A1:J1')

            _range_titles[0].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "Account's Balances"
            )

            _range_titles[2].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "Today's Account's Movement"
            )

            _range_titles[5].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "Transactions"
            )

            # Transaction Header's
            _range_headers = _worksheet_dashboard.range('F2:J2')
            _range_headers[0].value = "ID"
            _range_headers[1].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "DATE"
            )
            _range_headers[2].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "COST"
            )
            _range_headers[3].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "QUOTATION"
            )
            _range_headers[4].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                "USDT"
            )

            _range_transactions_total = _worksheet_dashboard.range('F6:J6')

            _range_transactions_total[0].value = GoogleTranslator(
                source='en',
                target=self._current_user.language).translate(
                'TOTAL'
            )
            _range_transactions_total[1].value = '=SUM(H3:H) * -1'
            _range_transactions_total[3].value = '=SUM(J3:J)'

            # MERGE RANGES AND UPDATE THEM!
            _range_titles.extend(_range_headers)
            _range_titles.extend(_range_transactions_total)
            _worksheet_dashboard.update_cells(_range_titles, value_input_option="USER_ENTERED")

            # FORMAT THIS SHIT!
            _worksheet_dashboard.format('A3:A4', currency_brl)
            _worksheet_dashboard.format('C3:C4', currency_brl)
            _worksheet_dashboard.format('H3:H', currency_brl)
            _worksheet_dashboard.format('I3:I', currency_usdt)
            _worksheet_dashboard.format('J3:J', currency_usdt)

            # COLORIZE THIS SHIT!
            _range_balance = 'A1:B1'
            _color_balance = Color.fromHex("#BFD6A9")
            _fmt_balance = CellFormat(
                backgroundColor=_color_balance,
            )

            _range_balance_value = 'A3:B3'
            _color_balance_value = Color.fromHex("#DDE9D2")
            _fmt_balance_value = CellFormat(
                backgroundColor=_color_balance_value,
            )

            _range_todays_balance = 'C1:D1'
            _color_todays_balance = Color.fromHex("#F7E49C")
            _fmt_todays_balance = CellFormat(
                backgroundColor=_color_todays_balance,
            )

            _range_todays_balance_value = 'C3:D3'
            _color_todays_balance_value = Color.fromHex("#FCF1CD")
            _fmt_todays_balance_value = CellFormat(
                backgroundColor=_color_todays_balance_value,
            )

            _range_transaction_separator = 'E1:E'
            _color_transaction_separator = Color.fromHex("#000000")
            _fmt_transaction_separator = CellFormat(
                backgroundColor=_color_transaction_separator,
            )

            _range_transactions_label = 'F1:F'
            _color_transactions_label = Color.fromHex("#EDC99D")
            _fmt_transactions_label = CellFormat(
                backgroundColor=_color_transactions_label,
            )

            _range_transaction_date = 'G2:G'
            _color_transaction_date = Color.fromHex("#EFEFEF")
            _fmt_transaction_date = CellFormat(
                backgroundColor=_color_transaction_date,
            )

            _range_transaction_cost = 'H2:H'
            _color_transaction_cost = Color.fromHex("#E3D0DA")
            _fmt_transaction_cost = CellFormat(
                backgroundColor=_color_transaction_cost,
            )

            _range_transaction_quotation = 'I2:I'
            _color_transaction_quotation = Color.fromHex("#D3DFE2")
            _fmt_transaction_quotation = CellFormat(
                backgroundColor=_color_transaction_quotation,
            )

            _range_transaction_usdt = 'J2:J'
            _color_transaction_usdt = Color.fromHex("#DDE9D2")
            _fmt_transaction_usdt = CellFormat(
                backgroundColor=_color_transaction_usdt,
            )

            format_cell_ranges(
                _worksheet_dashboard,
                [
                    (_range_balance, _fmt_balance),
                    (_range_balance_value, _fmt_balance_value),
                    (_range_todays_balance, _fmt_todays_balance),
                    (_range_todays_balance_value, _fmt_todays_balance_value),
                    (_range_transactions_label, _fmt_transactions_label),
                    (_range_transaction_date, _fmt_transaction_date),
                    (_range_transaction_cost, _fmt_transaction_cost),
                    (_range_transaction_quotation, _fmt_transaction_quotation),
                    (_range_transaction_usdt, _fmt_transaction_usdt),
                    (_range_transaction_separator, _fmt_transaction_separator)
                ]
            )

        return _worksheet_dashboard

    def dashboard_reload(self, dash_worksheet, sheet):
        balance_sum = "=SUM("
        today_balance_sum = "=SUM("
        today_day_month = f"{datetime.now().strftime('%d/%m')}"

        for _ws in sheet.worksheets(exclude_hidden=True):
            if re.match(r'^\d+/\d+$', _ws.title):

                for total_to_be_sum in _ws.findall('total', case_sensitive=False):
                    balance_end_column = re.sub(r'\d+', '', rowcol_to_a1(row=3, col=total_to_be_sum.col + 2))
                    balance_content = f"'{_ws.title}'!{rowcol_to_a1(row=3, col=total_to_be_sum.col + 2)}:{balance_end_column}; "
                    balance_sum += balance_content
                    if today_day_month == _ws.title:
                        today_balance_sum += balance_content

        today_balance_sum += ")"
        balance_sum += "G:G)"

        _balance_range = dash_worksheet.range("A3:C3")

        _balance_range[0].value = balance_sum
        _balance_range[2].value = today_balance_sum

        dash_worksheet.update_cells(_balance_range, value_input_option='USER_ENTERED')

        sheet.batch_update({
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": dash_worksheet.id,
                            "index": 0  # Move to the first position
                        },
                        "fields": "index"
                    }
                }
            ]
        })

    def create_or_retrieve_sheet(self, sheet_title, year, month, user_folder_id):

        
        if len(str(int(month))) <= 1:
            month = f"0{str(int(month))}"
        elif len(str(int(month))) > 2:
            month = f"{str(int(month))[:1]}"

        _statement_alias = f"{year}/{month}"

        _this_sheet_model = None
        _sheet = None
        _old_auth_emails = []
        is_a_new_sheet = False

        if self._current_user.google.sheets.get(_statement_alias) is not None:
            try:
                _sheet = gsheets.open_by_key(self._current_user.google.sheets.get(_statement_alias).external_id)
                _this_sheet_model = self._current_user.google.sheets.get(_statement_alias)
                _old_auth_emails = _this_sheet_model.authorized_emails
            except Exception as e:
                is_a_new_sheet = True
                print(e)
                pass

        if _sheet is None:

            if user_folder_id is not None:
                _sheet = gsheets.create(sheet_title, folder_id=user_folder_id)

            else:
                _sheet = gsheets.create(sheet_title)

            # save a notification for the user
            _notification_controller = NotificationController()

            _new_protocol = NotificationRequestModel(sub='root')
            _new_protocol.client_id = ObjectId(self._current_user.get_id())

            url = f"{Constants.url_google_sheets}{_sheet.id}"

            _new_protocol.content = f"[Notification] New sheet created!\n You can access it in a minute at: {url}\n{self._settings.get('root', 'attendant_default_response_request_attendance')}"

            _protocol_add_result = _notification_controller.add(_new_protocol)

            is_a_new_sheet = True

            _sheet.update_locale('pt_BR')

            self.check_for_unset_permissions()

            _this_sheet_model = GoogleSheet()
            _this_sheet_model.name = _statement_alias
            _this_sheet_model.external_id = _sheet.id
            _this_sheet_model.date = datetime.now().isoformat()

        
        if is_a_new_sheet:
            _this_sheet_model.authorized_emails = []

        elif len(self._current_user.google.sheets.get(_statement_alias).authorized_emails) < 1:
            
            try:
                _this_sheet_model.authorized_emails = [permission['emailAddress'] for permission in
                                                       _sheet.list_permissions()]
            except:
                pass

        _emails_has_changed = [email for email in _this_sheet_model.authorized_emails if email not in _old_auth_emails]

        if any([*_emails_has_changed]) or is_a_new_sheet:
            self.user_db.update(self._current_user_selector,
                                content={f"google.sheets.{_statement_alias}": _this_sheet_model.model_dump()})
        
        return _sheet

    def statement_retrieve_or_create_worksheet_for_the_day(self, worksheet_tab_name, _user_folder_id, sheet,
                                                           _statement_alias, skip_cols):

        self._current_user = self._retrieve_user_model()

        def create_headers():

            self._current_worksheet = sheet.add_worksheet(worksheet_tab_name, rows=1, cols=1)

            
            

            for inst in self._current_user.institutions:

                _institution_data = InstitutionRequestModel(
                    **self.institution_db.query({"_id": ObjectId(inst.institution_id)}))

                _starting_pos = self._current_worksheet.col_count + skip_cols
                if inst.status:
                    

                    self._current_worksheet.add_cols(len(self._default_statement_columns) + skip_cols)

                    # merge columns to add institution header label
                    self._current_worksheet.merge_cells(1, _starting_pos, 1, _starting_pos + len(
                        self._default_statement_columns) - skip_cols, merge_type='MERGE_ALL')

                    # set the label for the current institution on the merged cells
                    _range_institution = self._current_worksheet.range(
                        f"{rowcol_to_a1(row=1, col=_starting_pos)}:{rowcol_to_a1(row=1, col=_starting_pos + 1)}")
                    _range_institution[0].value = _institution_data.alias

                    if self._current_worksheet.row_count == 1:
                        # add row for statement columns
                        self._current_worksheet.add_rows(3)

                    # HEADERS
                    _headers_range = self._current_worksheet.range(
                        str(rowcol_to_a1(row=2, col=_starting_pos) + ":" + rowcol_to_a1(row=2, col=int(
                            _starting_pos + len(self._default_statement_columns)))))

                    _value_column_index = None
                    for _i, _cell in zip(range(len(self._default_statement_columns)), _headers_range):
                        _cell.value = str(GoogleTranslator(source='en', target=self._current_user.language).translate(
                            self._default_statement_columns[_i])).capitalize()
                        if self._default_statement_columns[_i] == 'value':
                            _value_column_index = _starting_pos + _i

                    _range_institution.extend(_headers_range)

                    # TOTAL FOOTER
                    _footer_value_merge = rowcol_to_a1(row=4, col=_starting_pos + 1)

                    self._current_worksheet.merge_cells(4, _starting_pos + 1, 4, _starting_pos + len(
                        self._default_statement_columns) - skip_cols, merge_type='MERGE_ALL')

                    # SET THE RANGE TO BE CALCULATED ON THE TOTAL
                    _footer_column_a1_notation_start = rowcol_to_a1(row=3, col=_value_column_index)
                    _footer_column_a1_notation_end = re.sub(r'\d+', '', rowcol_to_a1(row=3, col=_value_column_index))

                    # GENERATE THE CONTENT TO BE FILLED INTO THE TOTAL ROWS
                    _footer_content = [GoogleTranslator(source='en', target=self._current_user.language).translate(
                        'Total').capitalize(),
                                       f"=SUM({_footer_column_a1_notation_end}:{_footer_column_a1_notation_end})"]

                    _footer_range = self._current_worksheet.range(
                        str(rowcol_to_a1(row=4, col=_starting_pos) + ":" + rowcol_to_a1(row=4, col=int(
                            _starting_pos + len(_footer_content) - 1))))

                    for _i, _cell in zip(range(len(_footer_content)), _footer_range):
                        _cell.value = _footer_content[_i]

                    # SAVE THE CONTENT TO THE WS
                    _range_institution.extend(_footer_range)
                    self._current_worksheet.update_cells(_range_institution, value_input_option='USER_ENTERED')

                    _starting_pos += len(self._default_statement_columns)

                    self._current_worksheet = sheet.worksheet(worksheet_tab_name)

        def apply_theme():

            format = {
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE"
            }

            self._current_worksheet.format(':', format)

            for inst in self._current_user.institutions:

                if inst.status:
                    _this_institution_data = InstitutionRequestModel(
                        **self.institution_db.query({"_id": ObjectId(inst.institution_id)}))

                    _worksheet_inst_separator = self._current_worksheet.find(
                        _this_institution_data.alias.upper(),
                        in_row=1,
                        case_sensitive=False)

                    _range_inst = re.sub(r'\d+', '', rowcol_to_a1(1, _worksheet_inst_separator.col))

                    _color_inst_bg = Color.fromHex(_this_institution_data.style.background)

                    _color_inst_fg = Color.fromHex(_this_institution_data.style.color)

                    _fmt_inst = CellFormat(
                        backgroundColor=_color_inst_bg,
                        textFormat=TextFormat(bold=True, foregroundColor=_color_inst_fg),
                        horizontalAlignment='CENTER'
                    )

                    _range_indexes = rowcol_to_a1(2, _worksheet_inst_separator.col)

                    _fmt_indexes = CellFormat(
                        textFormat=TextFormat(bold=True)
                    )

                    print(f"Formatting Institutions on range: {_range_inst}")
                    _fmt_specs = [
                        (_range_inst, _fmt_inst),
                        (_range_indexes, _fmt_indexes)
                    ]

                    _current_col = 0

                    for child_index in range(len(self._default_statement_columns_colors)):

                        _range_child_index = re.sub(r'\d+', '',
                                                    rowcol_to_a1(1, _worksheet_inst_separator.col + child_index))

                        if self._default_statement_columns_colors[child_index] is not None:
                            _fmt_col = CellFormat(
                                backgroundColor=Color.fromHex(self._default_statement_columns_colors[child_index])
                            )

                            _fmt_specs.append((_range_child_index, _fmt_col))

                        if self._default_statement_columns_formatting[child_index] is not None:
                            self._current_worksheet.format(_range_child_index,
                                                           self._default_statement_columns_formatting[child_index])

                        _current_col += 1

                    format_cell_ranges(self._current_worksheet, _fmt_specs)

        def move_ws_to_first_pos():
            sheet.batch_update({
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": self._current_worksheet.id,
                                "index": 0  # Move to the first position
                            },
                            "fields": "index"
                        }
                    }
                ]
            })

        try:
            self._current_worksheet = sheet.worksheet(worksheet_tab_name)
        except:
            create_headers()
            
            apply_theme()
            
            if not self._already_send:
                # save a notification for the user
                _notification_controller = NotificationController()

                _new_protocol = NotificationRequestModel(sub='root')
                _new_protocol.client_id = ObjectId(self._current_user.get_id())

                url = f"{Constants.url_google_sheets}{self._current_worksheet.id}"

                _new_protocol.content = f"[Notification] New Worksheet Created!\n You can access it in a minute at: {url}\n{self._settings.get('root', 'attendant_default_response_request_attendance')}"

                _protocol_add_result = _notification_controller.add(_new_protocol)

                self._already_send = True

        move_ws_to_first_pos()
        return self._current_worksheet

    def sync_transaction(self):
        self._current_user = self._retrieve_user_model()
        _transactions_chunk = self.transaction_db.get_to_export_transactions(str(self._current_user.get_id()))

        def get_first_empty_row(ws):
            # Assuming 'sheet' is the worksheet you're working with
            # Define the range of columns (F to I)
            start_col = 'F'
            end_col = 'I'
            # Get all values in the specified range
            cell_range = f'{start_col}1:{end_col}'
            values = ws.get(cell_range)
            # Find the first empty row
            for i, row in enumerate(values):
                if all(cell == '' for cell in row):
                    # Empty row found, return row and column as integers
                    return i + 1, ord(start_col) - 64  # Row is 1-indexed, column is 0-indexed
            # If no empty row is found, return None

            return None

        def prepare_dataframe(_current_chunk):
            df = pd.DataFrame(_current_chunk)

            _settings = TransactionSettings()
            _clean_df = df.drop(columns=_settings.excluded_columns, errors='ignore')

            _clean_df['amount_from'] = _clean_df['amount_from'].astype(str).str.replace('.', ',')

            _clean_df = _clean_df[_settings.to_send]

            for original_name, desired_name in _settings.rename_columns.items():
                if original_name in _clean_df.columns:
                    _clean_df.rename(columns={original_name: desired_name}, inplace=True)

            for field in _settings.translated_columns:
                if field in _clean_df.columns:
                    _clean_df.rename(columns={field: str(
                        GoogleTranslator(source='en', target=self._current_user.language).translate(
                            field)).capitalize()}, inplace=True)

            return _clean_df

        if _transactions_chunk:

            df = pd.DataFrame(_transactions_chunk)
            df = StatementDataframeAdjustment(df).return_dataframe()

            for year in df['date'].dt.year.unique():
                logger('info', f"Processing statement year: {year}")

                for month in df[df['date'].dt.year == year]['date'].dt.month.unique():
                    month = int(month)
                    _this_month_statement = df[(df['date'].dt.month == month) & (df['date'].dt.year == year)]

                    sheet_title = self.generate_sheet_title(month, year)

                    _statement_alias = f"{year}/{month}"

                    _user_folder_id = self._current_user.get_google().drive.get('statement',
                                                                                GoogleDriveFolder()).external_id

                    print(f'\n\n\tRetrieving _sheet with {sheet_title, _statement_alias, _user_folder_id}\n\n')
                    _sheet = self.create_or_retrieve_sheet(sheet_title, year, month, _user_folder_id)

                    _worksheet_dashboard = self.generate_or_retrieve_new_dashboard(_sheet)

                    _clean_data = prepare_dataframe(df)

                    try:
                        _row, _col = get_first_empty_row(_worksheet_dashboard)
                    except:
                        _row_count_to_append = _clean_data.shape[0]
                        _worksheet_dashboard.insert_rows([[''] for _i in range(_row_count_to_append)],
                                                         row=int(_worksheet_dashboard.row_count),
                                                         inherit_from_before=True)
                        _row, _col = get_first_empty_row(_worksheet_dashboard)
                    logger('info', f"Set data on sheet: {_worksheet_dashboard}")
                    gd.set_with_dataframe(
                        worksheet=_worksheet_dashboard,
                        dataframe=_clean_data,
                        row=_row,
                        include_index=False,
                        include_column_header=False,
                        resize=False,
                        col=_col
                    )

                    self.dashboard_reload(sheet=_sheet, dash_worksheet=_worksheet_dashboard)

                    _a1_transactions = rowcol_to_a1(row=3, col=_col + 1) + ":" + "J" + str(
                        _worksheet_dashboard.row_count - 1)
                    print(_a1_transactions)

                    _exp_ids = list(df['_id'].to_list())
                    self.transaction_db.set_exportation_status(_exp_ids)

                    # try your 'sort'

                    # _worksheet_dashboard.sor((1, 'asc'), range=_a1_transactions)
                    # _worksheet_dashboard.batch_update(_sort_specs)
                    logger('info', f"Exported ids: {_exp_ids}")
                    return _exp_ids
