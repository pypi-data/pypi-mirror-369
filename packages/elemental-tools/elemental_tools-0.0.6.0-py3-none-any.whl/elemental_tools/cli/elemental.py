import argparse
import sys
import os
import shutil

from icecream import ic
from typing import Union

from elemental_tools.file_system import module_path
from elemental_tools.file_system import generate_env_file

further_info = "Type --help for further information."
provide_valid = "Please provide a valid"
sys.tracebacklimit = 0


def get_examples_path(sub_folder) -> os.path:
    abs_examples_path = os.path.join(module_path, 'examples', sub_folder)
    return abs_examples_path


def generate_docker_from_examples(destination_path: str, **variables) -> Union[bool, None]:
    abs_examples_path = get_examples_path('docker')

    if not os.path.isfile(os.path.join(destination_path, 'docker.env')):
        if os.path.isfile(os.path.join(destination_path, '.env')):
            shutil.copy(os.path.join(destination_path, '.env'), os.path.join(destination_path, 'docker.env'))

    for file in os.listdir(abs_examples_path):

        if os.path.isfile(os.path.join(abs_examples_path, file)):
            with open(os.path.join(abs_examples_path, file), 'r') as ex:

                content = ex.read()

                ic('before')
                ic(content)

                for variable, variable_content in variables.items():
                    ic(variable, variable_content)
                    content = content.replace(f"${str(variable)}", str(variable_content))

                ic('after')
                ic(content)

            if content is not None:
                ic(destination_path)
                ic(os.path.abspath(destination_path))

                try:
                    os.makedirs(os.path.abspath(destination_path), exist_ok=True)
                except:
                    raise Exception("Invalid Destination Path")

                with open(os.path.join(os.path.abspath(destination_path), file), 'w') as destination_file:
                    print(f"Saving file on {os.path.join(os.path.abspath(destination_path), file)}")
                    destination_file.write(content)

    return True


def main():
    from elemental_tools.logger import Logger
    logger = Logger(app_name='ELEMENTAL', owner='CLI').log

    parser = argparse.ArgumentParser(description='Example script with a database flag.')

    # Add the -db flag with a default value
    parser.add_argument('-i', '--install', '--upgrade', '--update', action='store_true', help='Create or update the database on the provided host. Check the read-me to see the .env file configurations.\n\tAlways recommended before updating the package itself.')
    parser.add_argument('-e', '--env_file',  default='.env',
                        help='Full path to a basic .env file as described on the read-me.')

    parser.add_argument('-docker', '--docker', action='store_true', default=False,
                        help='Generate Docker Files for the API Environment')

    parser.add_argument('-docker_user_folder_path', '--docker_user_folder_path', '-user_path', '--user_path', '-docker_user_folder_path', default='/docker_users',
                        help='Folder Path to where you want to persist docker user data.')

    parser.add_argument('-company_name', '--company_name', '-name', default=False,
                        help='Company Name for the Installation')

    parser.add_argument('-port', '--port', '-api_port', default=3000,
                        help='API Port for the Installation')

    parser.add_argument('-destination_path', '--destination_path', '-path', '--path', default='.',
                        help='Destination Path. Default = current directory.')

    parser.add_argument('-generate_env', '--generate_env', '-g_env', '--g_env', default=False,
                        action='store_true', help='Generate a Environment File on -destination_path.')

    parser.add_argument('-g_api', '-generate_api_files', '--generate_api_files', '-g_api_files', '--g_api_files', default=False,
                        action='store_true', help='Generate API File System on -destination_path.')


    # load arguments
    arguments = parser.parse_args()

    arg_dict = arguments.__dict__

    def install_database():
        if arguments.install and arguments.env_file:
            logger('info', f'Environment Variables: {str(os.environ.__dict__)}')

            from elemental_tools.Jarvis.install import InstallJarvis, InstallAPI
            from elemental_tools.datasets import install_datasets

            try:
                InstallJarvis().install()
                InstallAPI().install()
                install_datasets()
            except Exception as e:
                logger('error', f'Installation Failed: {str(e)}')

        elif arguments.install and not arguments.env_file:
            logger('error', f'{provide_valid} .env file via -e argument. {further_info}')

    def apply_database_settings():
        if arguments.company_name and arguments.env_file:
            from elemental_tools.api.settings import SettingsController, Setting
            from elemental_tools.config import root_user
            new_setting = Setting()
            new_setting.name = "company_name"
            new_setting.value = arguments.company_name
            SettingsController().set(sub=root_user, _setting=new_setting)

        if arguments.generate_env and arguments.company_name:
            generate_env_file(os.path.join(os.path.abspath(arguments.destination_path), '.env'), **arguments.__dict__)
        elif arguments.generate_env and not arguments.company_name:
            raise Exception(f"{provide_valid} company_name. {further_info}")

    def generate_docker():
        if arguments.docker and arguments.company_name:
            logger('info',
                   f"Generating Docker Files for {arguments.company_name} on path: {os.path.abspath(arguments.destination_path)}")

            generate_docker_from_examples(destination_path=arguments.destination_path, **arg_dict)
            logger('success',
                   f"Docker Files Generated Successfully")

        elif arguments.docker and not arguments.company_name:
            logger('error', f'{provide_valid} company_name. {further_info}')

    def generate_api_files() -> bool:
        if arguments.generate_api_files:
            abs_examples_path = get_examples_path('api')

            for file in os.listdir(abs_examples_path):
                if not os.path.isfile(os.path.join(arguments.destination_path, file)):

                    logger('info', f"Generating File: {os.path.join(arguments.destination_path, file)}")

                    try:
                        os.makedirs(arguments.destination_path, exist_ok=True)
                        shutil.copy(os.path.join(abs_examples_path, file), os.path.join(arguments.destination_path, file))
                    except:
                        logger('error', f"Failed to Generate File")
                else:
                    logger('alert', f"File {os.path.join(arguments.destination_path, file)} Already Exists, Skipping...")

            return True

        return False

    # load env file
    if arguments.env_file:
        from dotenv import load_dotenv
        load_dotenv(arguments.env_file)

    # set config for all methods
    if arg_dict['company_name']:
        arg_dict['app_name_pc_friendly'] = arg_dict['company_name'].lower().replace(' ', '_')
        arg_dict['elemental_package_path'] = os.path.dirname(os.path.dirname(__file__))

    install_database()
    apply_database_settings()
    generate_docker()
    generate_api_files()
