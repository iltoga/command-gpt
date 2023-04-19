from audio_transcriber import AudioTranscriber
import dotenv
import os
import queue
import threading
import signal
import sys

def handle_transcription(transcription):
    print("Audio transcription:")
    transcription_queue.put(transcription)
    transcription_event.set()

if __name__ == "__main__":
    dotenv.load_dotenv()

    speech_recognition_model = os.getenv("SPEECH_TO_TEXT_MODEL") or "jonatasgrosman/wav2vec2-large-xlsr-53-english"
    transcription_queue = queue.Queue()
    transcription_event = threading.Event()
    audio_transcriver = AudioTranscriber(
        speech_recognition_model=speech_recognition_model, 
        transcription_callback=handle_transcription,
    )

    while True:
        audio_transcriver.init()
        # Wait for the transcription to be completed
        transcription_event.wait()

        print("Transcription completed.")
        transcription_text = transcription_queue.get()
        print(transcription_text)
