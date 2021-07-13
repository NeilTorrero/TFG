import os
import subprocess
import sys
import requests


def getResponses(prediction):
    json_schema = '{"name": "' + prediction['intent']['name'] + '","entities": {'

    first = True
    for entity in prediction['entities']:
        if not first:
            json_schema += ','
        else:
            first = False
        json_schema += '"' + entity['entity'] + '": "' + entity['value'] + '"'

    json_schema += '}}'

    response = requests.post("http://localhost:5005/conversations/default/trigger_intent", json_schema)
    #print(response.json())
    return response.json()

def predictText(text):
    response = requests.post("http://localhost:5005/model/parse",
                             '{"text": "' + text + '"}')  # curl localhost:5005/model/parse -d '{"text":"I am mohit saini"}'
    # print(response.json())

    print(response.json()['intent_ranking'])
    print(response.json()['entities'])

    return response.json()


api_run = ""


def check_Run_Server():
    global api_run
    response = ""
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


def check_Kill_Server():
    global api_run
    if api_run != "":
        api_run.kill()
        print("API Server killed")
