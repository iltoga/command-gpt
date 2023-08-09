# main.py

import json
import os
import queue
import subprocess
import sys
import threading

from dotenv import load_dotenv
from jinja2 import Template
from pyagents import AudioTranscriber, CosineSimilarity

from command_matcher import CommandMatcher

sys.path.append("..")


def handle_transcription(transcription):
    print("Audio transcription:")
    transcription_queue.put(transcription)
    transcription_event.set()


def list_installed_applications():
    command = "mdfind 'kMDItemContentType==com.apple.application-bundle'"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        apps = output.split("\n")
        apps = [os.path.basename(app) for app in apps if app]
        return apps
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def get_env_variable(var_name, default_value):
    return os.getenv(var_name) or default_value


def main():
    load_dotenv()

    installed_applications = list_installed_applications()
    with open("datasets/installed_apps.json", "w") as file:
        json.dump(installed_applications, file)

    command_confidence_threshold = float(get_env_variable("COMMAND_CONFIDENCE", 0.3))
    application_confidence_threshold = float(get_env_variable("APPLICATION_CONFIDENCE", 0.4))
    speech_recognition_model = get_env_variable("SPEECH_TO_TEXT_MODEL", "jonatasgrosman/wav2vec2-large-xlsr-53-english")
    sentence_tranformer_model = get_env_variable("SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    command_parser_model = get_env_variable("COMMAND_PARSER_MODEL", "LLukas22/gpt4all-lora-quantized-ggjt")
    command_parser_model_ggml = get_env_variable("COMMAND_PARSER_MODEL_GGML", "ggjt-model.bin")

    transcription_queue = queue.Queue()
    transcription_event = threading.Event()

    audio_transcriver = AudioTranscriber(
        speech_recognition_model=speech_recognition_model,
        transcription_callback=handle_transcription,
    )

    query_matcher = CosineSimilarity(model_name=sentence_tranformer_model)

    matcher = CommandMatcher()
    corpus = matcher.load_voice_inputs()

    while True:
        audio_transcriver.start()

        transcription_event.wait()
        transcription_text = transcription_queue.get()
        print(f"Transcription completed: {transcription_text}")
        transcription_event.clear()

        best_match_command = query_matcher.semantic_search(corpus=corpus, query=transcription_text, top_k=1)[0]
        command_below_threshold = best_match_command[1] < command_confidence_threshold

        best_match_application = query_matcher.semantic_search(
            corpus=installed_applications, query=transcription_text, top_k=1
        )[0]
        application_name_below_threshold = best_match_application[1] < application_confidence_threshold

        print(f"Command best match with transcript: {best_match_command}")
        best_match_command = best_match_command[0]
        print(f"Application name best match with transcript: {best_match_application}")
        best_match_application = best_match_application[0]

        command, description = matcher.match_voice_input(voice_input=best_match_command)

        if command is None:
            print(f"Command not found in the dataset: {best_match_command}")
            continue

        command = ",".join(command)
        cmdToExecute = Template(command).render(application_name=best_match_application)
        cmdToExecute = cmdToExecute.split(",")
        print(f"Command to execute: {cmdToExecute}")

        if command_below_threshold or application_name_below_threshold:
            y_n = input(
                f"Command confidence below threshold. Do you want to execute the following command anyway?\n{cmdToExecute}\n(y/n)?"
            )
            if y_n.strip() != "y":
                continue

        try:
            subprocess.run(cmdToExecute)
        except Exception as e:
            print(f"Error executing command: {e}")
            continue


if __name__ == "__main__":
    main()
