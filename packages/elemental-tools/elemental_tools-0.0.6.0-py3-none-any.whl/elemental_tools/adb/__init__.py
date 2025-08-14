import os
import subprocess

from time import sleep
from urllib.parse import urlencode
from elemental_tools.adb.keymap import KeyMap, Devices

os.environ['TERM'] = 'xterm'


class ADB:
    _connected = False
    _authorized_devices = False
    _command = ['adb', '-s', '', 'shell']

    def __init__(self):

        self.command = ['adb', 'shell']

        # Get detailed information about connected devices
        devices_output = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True)
        self._devices_lines = devices_output.stdout.strip().split('\n')[1:]

        self._unauthorized_devices = [line.split()[0] for line in self._devices_lines if
                                    'device' in line and 'unauthorized' in line]

        if len(self._devices_lines):
            # Filter authorized devices
            self._authorized_devices = [line.split()[0] for line in self._devices_lines if
                                  'device' in line and 'unauthorized' not in line]

            # Select the first authorized device
            device_id = self._authorized_devices[0]

            # Set the ADB device ID for future commands
            os.environ['ADB_DEVICE_ID'] = device_id

            # Update the command with the device ID
            self._command[2] = device_id

            # Open ADB shell for the selected device
            self.execute_subprocess()
            _connected = True

        self.check()

    def execute_subprocess(self):
        self.adb_shell_process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                  text=True)

    def run(self, command):
        self.adb_shell_process.stdin.write(f"{command}\n")
        self.adb_shell_process.stdin.flush()
        self.adb_shell_process.communicate()

    def check(self):
        unauthorized_error = "No authorized devices connected via ADB."

        while not self._connected:
            try:
                if not self._authorized_devices:

                    try:
                        self.command[2] = self._unauthorized_devices[0]
                        self.execute_subprocess()
                    except:
                        unauthorized_error = "Failed to authorize a new device."

                    raise Exception(unauthorized_error)
                if not self._devices_lines:
                    raise Exception("No devices connected via ADB.")
            except Exception as e:
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')

                print('Waiting for ADB connection. Check instructions.')
                print(str(e))

                # Sleep for a short duration before the next iteration
                sleep(1)

        return True


def clean_phone(phone: str):
    return phone.replace(' ', '').replace("-", "")


def send_wpp_message(phone: str, message: str):
    _this_adb = ADB()

    url = f"https://api.whatsapp.com/send?phone={clean_phone(phone)}&{urlencode({'text': message})}"

    _this_adb.run(f'am start -a android.intent.action.VIEW -d "{url}" && sleep 2 && input tap {Devices.MotoG6Plus.WPP.send_message_with_keyboard_closed} && input tap {Devices.MotoG6Plus.WPP.send_written_message} && {KeyMap.back}')

    return True


def open_wpp_contact(phone: str):
    _this_adb = ADB()

    url = f"https://api.whatsapp.com/send?phone={clean_phone(phone)}&{urlencode({'text': ''})}"
    _this_adb.run(f'am start -W -a android.intent.action.VIEW -d"{url}"')

    return True
