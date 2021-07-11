import os
import subprocess
import sys

import requests
import signal

response = ""
api_run = ""
try:
    response = requests.get("http://localhost:5005/status")
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    print("API Server Down")
    print("run in shell the command rasa run --enable-api")
    proj_dir = os.path.dirname(sys.modules['__main__'].__file__)
    api_run = subprocess.Popen(['rasa', 'run', '--enable-api'], cwd=proj_dir + "/Rasa")

    while True:
        try:
            response = requests.get("http://localhost:5005/status")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue
        print("API Server is now Up")
        break
except requests.exceptions.HTTPError:
    print(" 4xx or 5xx")
    exit()

print("API Status:", response.status_code)


if api_run != "":
    api_run.kill()
    print("API Server killed")
