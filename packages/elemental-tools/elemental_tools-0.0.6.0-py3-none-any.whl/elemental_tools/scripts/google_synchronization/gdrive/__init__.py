from __future__ import print_function
import re
from elemental_tools.patterns import Patterns
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from elemental_tools.scripts.google_synchronization.gsheet import google_credentials

version = 'v3'


def create_folder(folder_name, parent_id: list = None):
    try:
        # create drive api client
        service = build('drive', version, credentials=google_credentials)

        if parent_id:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': parent_id
            }
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
            }

        file = service.files().create(body=file_metadata, fields='id').execute()
        print(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def set_folder_permissions(folder_id, email_list):
    try:
        # create drive api client
        service = build('drive', version, credentials=google_credentials)
        _result = []

        for email in email_list:
            if re.match(Patterns.email, email):
                permissions = {'type': 'user', 'role': 'writer', 'emailAddress': email}
                response = service.permissions().create(fileId=folder_id, body=permissions).execute()
                _result.append(email)

        return _result

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def get_folder_id(folder_name, parent_id=None):
    try:
        service = build('drive', version, credentials=google_credentials)
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"

        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(q=query).execute()
        files = results.get('files', [])

        return files[0]['id']

    except Exception as error:
        print(f'An error occurred: {error}')
        return False

