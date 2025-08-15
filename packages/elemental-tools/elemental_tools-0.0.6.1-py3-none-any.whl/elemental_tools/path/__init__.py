import argparse
import os
from datetime import datetime


class Relative:

    def __init__(self, origin: str = __file__):
        self.origin = origin

    def relative(self, path):
        return os.path.join(os.path.dirname(self.origin), path)


def fix_sequential_names(folder_path, prefix=None, suffix=None):
    """
    Rename items in a folder with sequential numbers based on their date_modified.

    Parameters:
    - folder_path (str): Path to the target folder.

    Returns:
    None
    """

    # Retrieve a list of files and folders in the specified folder
    items = os.listdir(folder_path)

    # Filter out subdirectories
    files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]

    # Sort files based on their date_modified
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))

    # Rename files sequentially
    for index, filename in enumerate(sorted_files):
        file_path = os.path.join(folder_path, filename)

        # Extract the file extension (if any)
        _, file_extension = os.path.splitext(filename)

        new_filename = ""
        if prefix is not None:
            new_filename += f"{prefix}_"

        new_filename += f"{index + 1}"

        if suffix is not None:
            new_filename += f"_{suffix}"

        new_filename += f"{file_extension}"

        # Construct the new path
        new_file_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(file_path, new_file_path)


def sequential_rename_files():
    parser = argparse.ArgumentParser(description=f'Rename files sequentially to a specified format.')
    parser.add_argument('folder', help='Path to the folder you want to sequentially rename')
    parser.add_argument('--prefix', default=None, help='Prefix you want to add on each file')
    parser.add_argument('--suffix', default=None, help='Suffix you want to add on each file')

    args = parser.parse_args()

    fix_sequential_names(args.folder, args.prefix, args.suffix)
