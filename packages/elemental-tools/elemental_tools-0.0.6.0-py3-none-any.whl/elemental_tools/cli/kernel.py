import argparse
import os
from elemental_tools.logger import Logger

_log = Logger(app_name="Elemental-Tools", owner="cli").log


class ArgumentParser(argparse.ArgumentParser):
    description = ""
    _discard_from_action_on_concatenate = ['container', 'option_strings', 'nargs', 'const']

    def __init__(self):
        super().__init__()

        self.add_argument('input_path', help='Path to the input folder or file containing images')
        self.add_argument('--output_path', '-o', default=None,
                          help='Path to the output folder for the processed image(s)')

        # Recursion
        self.add_argument('--recursive', '-R', default=None, action='store_true',
                          help='Search for folders and subfolders')

        # Allowance
        self.add_argument('--yes', '-y', default=None, action='store_true', help='Ignore any alert')

        # Debug
        self.add_argument('--debug', '-d', default=None, action='store_true', help='Start with the verbose mode')

    def include_options(self, *to_include):

        for method in to_include:
            for action in method._actions:

                kwargs = {k_name: k_value for k_name, k_value in action.__dict__.items() if
                          k_name not in self._discard_from_action_on_concatenate}

                if [option_string for option_string in action.option_strings if option_string not in [option_string for sublist in self._actions for option_string in sublist.option_strings if option_string]]:
                    self.add_argument(*action.option_strings, **kwargs)


class CLI:
    parser: ArgumentParser = ArgumentParser()

    not_found = True
    junk = []
    supported_formats = []

    args = None
    dst = None
    user_path = None

    def __init__(self):
        pass

    def process_arguments(self):
        self.args = self.parser.parse_args()
        self.user_path = os.path.join(str(self.args.input_path))

        _min_resolution_tuple = tuple()

        if self.args.output_path is not None:
            self.dst = os.path.join(str(self.args.output_path))
            if os.path.isdir(self.args.output_path) and not self.args.yes:
                self.prompt_overwrite()

        # Check if none of the specified arguments are set
        if all(value is None for arg, value in vars(self.args).items() if arg != "input_path"):
            _log("alert", f"No valid command found. Type --help for assistance.")
            print(self.parser.format_help())

        else:
            if os.path.isdir(self.user_path):
                _log("info", f"Processing folder {self.user_path}")
                try:
                    self._recursive(self.user_path, self.dst)
                except Exception as e:
                    _log("error", f"An error occurred processing {self.user_path}\n{str(e)}", origin="kernel")

            else:
                _log("info", f"Processing file {self.user_path}", origin="kernel")
                try:
                    self.run(self.user_path, self.dst)
                except Exception as e:
                    _log("error",
                         f"An error occurred processing {self.user_path}\n{str(e)}",
                         origin="kernel")

            if self.not_found:
                _log("alert",
                     f"No compatible files found!",
                     origin="kernel")

    def _recursive(self, path, destination):

        if path not in self.junk:
            
            for each_file_folder in os.listdir(path):
                
                file_folder_path = os.path.join(path, each_file_folder)

                destination_path = os.path.join(destination, each_file_folder)

                # handle file
                if any(each_file_folder.lower().endswith(fmt) for fmt in self.supported_formats):
                    
                    if file_folder_path not in self.junk:  # Avoid processing the same file
                        
                        self.run(file_folder_path, destination_path)
                        self.not_found = False
                        
                        self.junk.append(file_folder_path)

                # handle folder
                elif os.path.isdir(file_folder_path) and os.listdir(file_folder_path):
                    if self.args.recursive:
                        self.junk.append(os.path.abspath(destination_path))
                        if not os.path.exists(str(destination_path)):
                            os.makedirs(str(destination_path), exist_ok=True)
                        self._recursive(file_folder_path, destination_path)

    def prompt_overwrite(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        overwrite = input(
            "The destination folder already exists, are you sure you want to overwrite its content? Type YES and hit enter to proceed.\nHit CTRL + C or CMD + C to skip execution.\n")
        if not overwrite == "YES":
            self.prompt_overwrite()
        else:
            return True

    def run(self, *args):
        return None


