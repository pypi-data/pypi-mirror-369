import shutil
import os
import pandas as pd
import json
from bs4 import BeautifulSoup
from io import StringIO

from icecream import ic

from elemental_tools.file_system.extensions import CSV, HTML, Undefined, JSON

module_path = os.path.dirname(os.path.dirname(__file__))


def copytree_with_error_handling(src, dst, symlinks=False, ignore=None):
    try:
        shutil.copytree(src=src, dst=dst, symlinks=symlinks, ignore=ignore)
    except shutil.Error as e:
        for src, dst, reason in e.args[0]:
            if os.path.exists(src):
                print(f"Failed to copy: {src} to {dst} - Reason: {reason}")
            else:
                print(f"Source file not found: {src}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return dst


def is_file_format(content: str):
    possible_csv_separators = [',', ';']
    for sep in possible_csv_separators:
        try:
            # Attempt to parse as CSV
            string_stream = StringIO(content)
            csv_df = pd.read_csv(string_stream, sep=sep, low_memory=False)
            if len(csv_df):
                return CSV
        except (pd.errors.ParserError, pd.errors.EmptyDataError, pd.errors.DtypeWarning):
            pass

    try:
        # Attempt to parse as HTML
        soup = BeautifulSoup(content, 'html.parser')
        return HTML
    except (TypeError, AttributeError):
        pass

    try:
        # Attempt to parse as JSON
        json.loads(content)
        return JSON
    except json.JSONDecodeError:
        pass

    # None of the above
    return Undefined


def generate_instance_folder_tree():
    folders = [
        'scripts',
        'grimoires'
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def generate_env_file(dst, **kwargs):

    sample_dot_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.env')
    with open(sample_dot_env, 'r') as dot_env_content:
        content = dot_env_content.read()

    if content is not None:
        for variable, variable_content in kwargs.items():
            content = content.replace(f"${variable}", str(variable_content))

    with open(dst, 'w') as dst_env_file:
        dst_env_file.write(content)


