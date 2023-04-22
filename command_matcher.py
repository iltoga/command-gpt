# The CommandMatcher class provides a convenient interface for matching text strings to a list of commands.
# It loads a list of commands and installed apps from JSON files and provides several methods for working with the loaded data. 
import json
import os

class CommandMatcher:
    def __init__(self, file_path='datasets'):
        self.file_path_commands = f'{file_path}/commands.json'
        self.file_path_installed_apps = f'{file_path}/installed_apps.json'
        self.commands = self.load_commands(self.file_path_commands)
        self.installed_apps = self.load_app_list()

    # Loads a list of commands from a JSON file. The function takes in a file path and a command type 
    # as arguments, where the command type is used to select a subset of commands from the file.
    def load_commands(self, file_path='datasets/commands.json', commands_type='process_control_commands'):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        if commands_type not in data:
            raise ValueError(f"Invalid commands_type: {commands_type}")
        return data[commands_type]

    # Loads a list of installed apps from a JSON file.
    def load_app_list(self):
        if not os.path.exists(self.file_path_commands):
            raise FileNotFoundError(f"File not found: {self.file_path_commands}")

        with open(self.file_path_commands, 'r') as file:
            app_list = json.load(file)
        return app_list

    # Returns a list of voice inputs for the loaded commands.
    def load_voice_inputs(self):
        voice_inputs = [voice_input for command in self.commands for voice_input in command['voice_input']]
        return voice_inputs

    # Matches a given voice input to a command in the loaded list of commands.
    def match_voice_input(self, voice_input):
        matched_command = next((command for command in self.commands if voice_input in command['voice_input']), None)
        if matched_command:
            return matched_command['command'], matched_command['description']
        return None, None

if __name__ == '__main__':
    # Example usage
    matcher = CommandMatcher()
    voice_inputs = matcher.load_voice_inputs()

    voice_input = "open Safari"
    command, description = matcher.match_voice_input(voice_input)
    print(command, description)
