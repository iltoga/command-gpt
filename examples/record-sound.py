import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pynput import keyboard

# Choose the sampling frequency
fs = 44100

# Initialize global variables
recording = []
is_recording = False
stream = None

# Define a callback function to record audio
def audio_callback(indata, frames, time, status):
    if is_recording:
        recording.append(indata.copy())

# Define a function that starts or stops recording when the spacebar key is pressed
def on_press(key):
    global is_recording
    global stream

    if key == keyboard.Key.space:
        if not is_recording:
            # Print message that recording has started
            print("Recording started...")

            # Start recording audio from the default microphone
            is_recording = True
            stream = sd.InputStream(samplerate=fs, channels=1, callback=audio_callback)
            stream.start()
        else:
            # Stop recording
            is_recording = False
            stream.stop()
            stream.close()

            # Save the recording to a wav file
            audio_data = np.concatenate(recording, axis=0)
            write('output.wav', fs, audio_data)

            # Print message that recording has stopped
            print("Recording stopped.")

            # Stop the listener and exit the program
            listener.stop()
            return False

# Start a keyboard listener that runs in a separate thread
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()  # Wait for the listener to finish (i.e. for the spacebar key to be pressed)
