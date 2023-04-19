import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pynput import keyboard
from huggingsound import SpeechRecognitionModel
import signal
import sys


class AudioTranscriber:
    def __init__(self, speech_recognition_model, transcription_callback=None):
        self.fs = 44100
        self.recording = []
        self.is_recording = False
        self.stream = None
        self.model = SpeechRecognitionModel(speech_recognition_model)
        self.listener = None
        self._initialize_signal_handler()
        self.transcription_callback = transcription_callback

    def create_stream(self):
        return sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)

    def transcribe(self, audio_file):
        transcriptions = self.model.transcribe([audio_file])
        return transcriptions[0]["transcription"]

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording.append(indata.copy())

    def on_press(self, key):
        if key == keyboard.Key.space:
            if not self.is_recording:
                print("Recording started...")
                self.is_recording = True
                self.stream = self.create_stream()
                self.stream.start()
            else:
                self.stop_recording()
        elif key == keyboard.Key.esc:
            self.stop_recording()
            return False

    def stop_recording(self):
        transcription = None
        if self.is_recording:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            audio_data = np.concatenate(self.recording, axis=0)
            output_file = 'output.wav'
            write(output_file, self.fs, audio_data)
            print("Recording stopped.")
            transcription = self.transcribe(output_file)
            os.remove(output_file)
            if self.transcription_callback:
                self.transcription_callback(transcription)

            # Clear the recording data
            self.recording = []

        if self.listener:
            self.listener.stop()
        return transcription


    def init(self):
        with keyboard.Listener(on_press=self.on_press) as self.listener:
            self.listener.join()

    def _initialize_signal_handler(self):
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        print("\nClosing AudioTranscriber...")
        self.stop_recording()
        sys.exit(0)
