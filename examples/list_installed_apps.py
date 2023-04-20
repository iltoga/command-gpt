import os
import subprocess

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

installed_applications = list_installed_applications()
print(installed_applications)
# write them to a file: datasets/installed_apps.json
import json

with open('datasets/installed_apps.json', 'w') as file:
    json.dump(installed_applications, file)

