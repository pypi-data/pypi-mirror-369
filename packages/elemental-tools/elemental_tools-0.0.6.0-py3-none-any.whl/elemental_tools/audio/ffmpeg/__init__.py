import os
import sys

from elemental_tools.logger import Logger
from elemental_tools.system import run_cmd

_log = Logger(app_name="Elemental-Tools", owner='ffmpeg').log


class Installations:

    ffmpeg = False
    portaudio = False
    pyaudio = False

    def __init__(self):
        _log('info', 'Checking audio dependencies')

        self.check_dependencies()

        if not self.ffmpeg:
            self.ffmpeg = run_cmd('brew install ffmpeg')
        if not self.pyaudio:
            self.portaudio = run_cmd("brew install portaudio")
            self.pyaudio = run_cmd("pip install pyaudio")

        if self.portaudio:
            _log('success', 'Portaudio Installed!')
        else:
            _log('critical-error',
                 'Failed to install Portaudio, please try installing manually. If it is not possible, you can check out for help on our github repo.')

        if self.pyaudio:
            _log('success', 'Updating PYAudio')
        else:
            _log('critical-error',
                 'Failed to install PYAudio, please try installing manually. If it is not possible, you can check out for help on our github repo.')

        if self.ffmpeg:
            _log('success', 'FFmpeg Installed!')
        else:
            _log('critical-error',
                 'Failed to install FFmpeg, please try installing manually. If it is not possible, you can check out for help on our github repo.')

    def check_dependencies(self):

        # check pyaudio
        try:
            import pyaudio
            self.pyaudio = True
            self.portaudio = True
        except:
            self.pyaudio = False

        # check ffmpeg
        if all([run_cmd('ffmpeg --help'), run_cmd('ffprobe --help')]):
            self.ffmpeg = True
        else:
            self.ffmpeg = False


class FFMPEG:

    _cwd = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        if sys.platform == 'darwin':

            if run_cmd('brew --help'):
                Installations()

            # os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            # sys.path.append('/opt/homebrew/bin/brew')
            # os.system('brew install ffmpeg')

            _darwin_path = os.path.join(self._cwd, 'darwin/')
            sys.path.append(_darwin_path)

        elif sys.platform == 'win32':
            _win32_path = os.path.join(self._cwd, 'win32/')
            sys.path.append(_win32_path)

        else:
            raise Exception("It seems that your plataform aren't compatible with our available encode module. Which is FFmpeg. Try to manualy install it, or call for some help on our github repo.")


def ffmpeg():
    FFMPEG()

