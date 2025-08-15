import os

from elemental_tools.config import csv_path

from elemental_tools.db.mongo import database
from elemental_tools.api.controllers.transaction import TransactionController

files_controller = database.collection("files")
transaction_controller = TransactionController()


def start(uid):

    if not os.path.isdir(csv_path):
        raise Exception("Invalid CSV Path")

    for file in os.listdir(csv_path):
        abs_path =
        transaction_controller.query({})

