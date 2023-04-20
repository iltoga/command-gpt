from audio_transcriber import AudioTranscriber
from cosine_similarity import CosineSimilarity
from command_matcher import CommandMatcher
from command_parser import CommandParser
import dotenv
import os
import queue
import threading
import subprocess
import json

def handle_transcription(transcription):
    print("Audio transcription:")
    transcription_queue.put(transcription)
    transcription_event.set()

# TODO: Move this to a separate file and implement version for other OSs
def list_installed_applications():
    command = "mdfind 'kMDItemContentType==com.apple.application-bundle'"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        apps = output.split('\n')
        apps = [os.path.basename(app) for app in apps if app]
        return apps
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    dotenv.load_dotenv()

    # Write the list of installed applications to a file, to be used by the command matcher
    installed_applications = list_installed_applications()
    with open('datasets/installed_apps.json', 'w') as file:
        json.dump(installed_applications, file)

    # For text to speech
    speech_recognition_model = os.getenv("SPEECH_TO_TEXT_MODEL") or "jonatasgrosman/wav2vec2-large-xlsr-53-english"
    # For sentence embedding and similarity search
    sentence_tranformer_model = os.getenv("SENTENCE_TRANSFORMER_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
    # For command parsing
    command_parser_model = os.getenv("COMMAND_PARSER_MODEL") or "LLukas22/gpt4all-lora-quantized-ggjt"
    command_parser_model_ggml = os.getenv("COMMAND_PARSER_MODEL_GGML") or "ggjt-model.bin"
    transcription_queue = queue.Queue()
    transcription_event = threading.Event()
    audio_transcriver = AudioTranscriber(
        speech_recognition_model=speech_recognition_model, 
        transcription_callback=handle_transcription,
    )

    query_matcher = CosineSimilarity(model_name=sentence_tranformer_model)

    # Load the dataset of sentences to match against the transcription
    matcher = CommandMatcher()
    corpus = matcher.load_voice_inputs()

    command_parser = CommandParser(model_name=command_parser_model_ggml, repo_id=command_parser_model)

    while True:
        audio_transcriver.start()

        # Wait for the transcription to be completed
        transcription_event.wait()
        transcription_text = transcription_queue.get()
        print(f"Transcription completed: {transcription_text}")
        transcription_event.clear()

        # Find the best match for the command
        best_match_command = query_matcher.semantic_search(corpus=corpus, query=transcription_text, top_k=1)[0]
        if best_match_command[1] < 0.3:
            print(f"Transcript does not rank well enough to run a command: {best_match_command}")
            continue

        # Find the best match for the application name in the transcription
        best_match_application = query_matcher.semantic_search(corpus=installed_applications, query=transcription_text, top_k=1)[0]
        if best_match_application[1] < 0.5:
            print(f"Application name does not rank well enough to run a command: {best_match_application}")
            continue


        print(f"Transcript best match: {best_match_command}")
        best_match_command = best_match_command[0]
        print(f"Application name best match: {best_match_application}")
        best_match_application = best_match_application[0]
        # Match the transcription to a generic command
        command, description = matcher.match_voice_input(voice_input=best_match_command)
        print(f"Command: {command}")

        # Run the command
        cmdToExecute = command_parser.GenerateText(command, best_match_application, prompt_template="parse_command")

        # command = "['open', '-a', 'Chrome.app']"
        # cmdToExecute = command_parser.GenerateCommand(command, "open safari")
        print(f"Command to execute: {cmdToExecute}")

        # try execute the command
        try:
            subprocess.run(cmdToExecute)
        except Exception as e:
            print(f"Error executing command: {e}")
            continue
