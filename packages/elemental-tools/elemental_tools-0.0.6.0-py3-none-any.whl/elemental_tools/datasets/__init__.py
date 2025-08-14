import os

import numpy as np
import pandas as pd
from bson import ObjectId

from elemental_tools.db.mongo import Connect
from elemental_tools.config import db_url, database_name, logger, root_user
from elemental_tools.api.settings import SettingsController, Setting
from elemental_tools.api.controllers.user import UserController

current_file_path = os.path.abspath(__file__)
user_controller = UserController()


def newest_version_available(current_folder_path=os.path.dirname(current_file_path)):
    this_version = -1
    with open(os.path.join(current_folder_path, ".version"), 'r') as version_file:
        this_version = int(version_file.read().replace('.', ''))

    return this_version


_root_id = None


def process_id(value):
    global _root_id

    result = None
    try:
        result = ObjectId(value)
    except:
        if value == root_user and _root_id is None:
            _root_id = root_user
            return root_user
        else:
            result = _root_id

    return result


def install_datasets(current_folder_path=os.path.dirname(current_file_path)):

    logger("start", "Checking for datasets upgrade...")
    settings_controller = SettingsController()

    version_database = settings_controller.get(root_user, 'version_database', default=0)

    if newest_version_available() > version_database:
        logger("alert", "Database being updated, please do a double check for consistency.")
        csv_files = [os.path.join(current_folder_path, str(e)) for e in os.listdir(current_folder_path) if e.lower().endswith('.json')]
        mongo_db = Connect(db_url, database_name)

        for file in csv_files:

            # Create a collection based on the CSV file name
            collection_name = os.path.basename(file).lower().replace('.json', '')
            logger("info", f"Installing: {collection_name}")
            this_collection = mongo_db.collection(collection_name)

            logger("info", f"Reading csv...")
            # Read CSV file into a Pandas DataFrame

            df = pd.read_json(file)
            df = df.replace(np.nan, None)

            if '_id' in df.columns:
                df['_id'] = df['_id'].apply(lambda x: process_id(x) if x is not None else None)

            if 'sub' in df.columns:
                df['sub'] = df['sub'].apply(lambda x: process_id(x) if x is not None else None)

            # Convert DataFrame to a list of dictionaries (each dictionary represents a row)
            data = df.to_dict(orient='records')

            logger("info", f"Inserting {data}")
            # Insert data into the MongoDB collection
            try:
                this_collection.insert_many(data)
            except Exception as e:
                logger("critical-error", f"Failed because of exception: {e}")

        logger("success", f"Database upgrade finish successfully!")
        new_version = Setting(name='version_database', value=newest_version_available())
        SettingsController().set(root_user, new_version)

        return True

    return False

