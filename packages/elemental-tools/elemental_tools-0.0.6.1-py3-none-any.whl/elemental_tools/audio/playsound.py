# Updated code
from pydub import AudioSegment
from pydub.playback import play


def playsound(file_path):
    audio = AudioSegment.from_file(file_path)
    play(audio)