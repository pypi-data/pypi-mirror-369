import speech_recognition as sr

# convert mp3 file to wav
# sound = AudioSegment.from_ogg("input/path.ogg")
# sound.export("transcript.wav", format="wav")
#
#
# # transcribe audio file
AUDIO_FILE = "/Users/antonioandriettineto/Desktop/Texto de tartaruga-001.wav"
#
# # use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
        print("Transcription: " + r.recognize_google(audio, language='pt'))
