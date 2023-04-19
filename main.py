from audio_recorder import AudioRecorder
import dotenv
import os

if __name__ == "__main__":
    dotenv.load_dotenv()
    
    speech_recognition_model = os.getenv("SPEECH_TO_TEXT_MODEL") or "jonatasgrosman/wav2vec2-large-xlsr-53-english"
    audio_recorder = AudioRecorder(speech_recognition_model=speech_recognition_model)
    audio_recorder.init()